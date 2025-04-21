from typing import List, Dict, Any, Optional
import asyncio
import time
from loguru import logger

from app.core.config import settings
from app.db.graph_db import graph_db
from app.db.vector_db import vector_db
from app.services.embedding_service import embedding_service


class GraphRAGService:
    """
    Service that combines graph and vector search for retrieval-augmented generation.
    """

    def __init__(self):
        """
        Initialize the GraphRAG service.
        """
        self.top_k_vector = settings.TOP_K_VECTOR
        self.top_k_graph = settings.TOP_K_GRAPH

    async def search(
        self, 
        query: str,
        search_type: str = "hybrid",
        filters: Optional[Dict[str, Any]] = None,
        pmqa_reference: Optional[Dict[str, str]] = None,
        top_k: int = 10,
        vector_weight: float = 0.5,
        graph_weight: float = 0.5
    ) -> Dict[str, Any]:
        """
        Search for relevant documents and chunks based on query.
        
        Args:
            query: Search query
            search_type: Type of search ("vector", "graph", or "hybrid")
            filters: Optional filters for search
            pmqa_reference: Optional PMQA reference to focus the search
            top_k: Number of top results to return
            vector_weight: Weight for vector search results (0-1) for hybrid search
            graph_weight: Weight for graph search results (0-1) for hybrid search
            
        Returns:
            Search results
        """
        start_time = time.time()
        
        try:
            # Initialize results
            results = []
            
            if search_type == "vector":
                # Vector search only
                results = await self._vector_search(query, filters, top_k)
            elif search_type == "graph":
                # Graph search only
                results = await self._graph_search(query, filters, pmqa_reference, top_k)
            else:
                # Hybrid search (default)
                results = await self._hybrid_search(
                    query, filters, pmqa_reference, top_k, vector_weight, graph_weight
                )
            
            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000
            
            return {
                "query": query,
                "total_results": len(results),
                "results": results,
                "search_type": search_type,
                "execution_time_ms": execution_time_ms
            }
        except Exception as e:
            logger.error(f"Error in GraphRAG search: {str(e)}")
            raise

    async def _vector_search(
        self, 
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform vector search.
        
        Args:
            query: Search query
            filters: Optional filters for search
            top_k: Number of top results to return
            
        Returns:
            List of search results
        """
        try:
            # Create embedding for query
            query_embedding = embedding_service.create_embedding(query)
            
            # Convert filters to Chroma format if provided
            where_filter = self._convert_filters_to_chroma(filters)
            
            # Search chunks
            results = vector_db.search_chunks(
                query_text=query,
                n_results=top_k,
                where_filter=where_filter
            )
            
            # Process results
            processed_results = []
            
            if results and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    chunk_id = results["ids"][0][i]
                    document = results["metadatas"][0][i]
                    content = results["documents"][0][i]
                    score = float(results["distances"][0][i]) if "distances" in results else 0.0
                    
                    # Convert score to similarity (1 - distance)
                    similarity = 1.0 - score
                    
                    processed_results.append({
                        "document_id": document.get("document_id", ""),
                        "document_title": document.get("title", ""),
                        "chunk_id": chunk_id,
                        "content": content,
                        "score": similarity,
                        "pmqa_references": document.get("pmqa_references", []),
                        "metadata": {
                            key: val for key, val in document.items()
                            if key not in ["document_id", "pmqa_references"]
                        }
                    })
            
            return processed_results
        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            return []

    async def _graph_search(
        self, 
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        pmqa_reference: Optional[Dict[str, str]] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform graph search.
        
        Args:
            query: Search query
            filters: Optional filters for search
            pmqa_reference: Optional PMQA reference to focus the search
            top_k: Number of top results to return
            
        Returns:
            List of search results
        """
        try:
            # Create Cypher query for graph search
            cypher_query, params = self._build_graph_query(query, filters, pmqa_reference, top_k)
            
            # Execute query
            results = graph_db.execute_read_query(cypher_query, params)
            
            # Process results
            processed_results = []
            
            for result in results:
                chunk = result.get("chunk", {})
                document = result.get("document", {})
                score = result.get("score", 0.0)
                
                # Get PMQA references
                pmqa_refs = []
                if "pmqaRefs" in result:
                    for ref in result["pmqaRefs"]:
                        if ref:
                            pmqa_refs.append({
                                "category_id": ref.get("category_id", ""),
                                "category_name": ref.get("category_name", ""),
                                "subcategory_id": ref.get("subcategory_id", ""),
                                "subcategory_name": ref.get("subcategory_name", ""),
                                "criteria_id": ref.get("criteria_id", ""),
                                "criteria_name": ref.get("criteria_name", "")
                            })
                
                processed_results.append({
                    "document_id": document.get("id", ""),
                    "document_title": document.get("title", ""),
                    "chunk_id": chunk.get("id", ""),
                    "content": chunk.get("content", ""),
                    "score": score,
                    "pmqa_references": pmqa_refs,
                    "metadata": {
                        "path": document.get("path", ""),
                        "mimetype": document.get("mimetype", ""),
                        "created_at": document.get("created_at", ""),
                        "modified_at": document.get("modified_at", "")
                    }
                })
            
            return processed_results
        except Exception as e:
            logger.error(f"Error in graph search: {str(e)}")
            return []

    async def _hybrid_search(
        self, 
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        pmqa_reference: Optional[Dict[str, str]] = None,
        top_k: int = 10,
        vector_weight: float = 0.5,
        graph_weight: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search, combining vector and graph search.
        
        Args:
            query: Search query
            filters: Optional filters for search
            pmqa_reference: Optional PMQA reference to focus the search
            top_k: Number of top results to return
            vector_weight: Weight for vector search results (0-1)
            graph_weight: Weight for graph search results (0-1)
            
        Returns:
            List of search results
        """
        try:
            # Run vector and graph search in parallel
            vector_results_task = asyncio.create_task(
                self._vector_search(query, filters, top_k * 2)
            )
            graph_results_task = asyncio.create_task(
                self._graph_search(query, filters, pmqa_reference, top_k * 2)
            )
            
            # Wait for both searches to complete
            vector_results = await vector_results_task
            graph_results = await graph_results_task
            
            # Combine and re-rank results
            combined_results = self._combine_results(
                vector_results, graph_results, 
                vector_weight, graph_weight, 
                top_k
            )
            
            return combined_results
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return []

    def _convert_filters_to_chroma(
        self, 
        filters: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Convert filters to Chroma format.
        
        Args:
            filters: Filters in API format
            
        Returns:
            Filters in Chroma format
        """
        if not filters:
            return None
        
        chroma_filters = {}
        
        # Map filters to Chroma format
        for key, value in filters.items():
            if key == "category":
                chroma_filters["category"] = value
            elif key == "published_after":
                chroma_filters["published_date"] = {"$gte": value}
            elif key == "published_before":
                chroma_filters["published_date"] = {"$lte": value}
            elif key == "author":
                chroma_filters["author"] = value
            elif key == "keywords":
                # Not directly supported in Chroma - would need a different approach
                pass
            else:
                # Pass through other filters directly
                chroma_filters[key] = value
        
        return chroma_filters if chroma_filters else None

    def _build_graph_query(
        self, 
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        pmqa_reference: Optional[Dict[str, str]] = None,
        top_k: int = 10
    ) -> tuple:
        """
        Build Cypher query for graph search.
        
        Args:
            query: Search query
            filters: Optional filters for search
            pmqa_reference: Optional PMQA reference to focus the search
            top_k: Number of top results to return
            
        Returns:
            Tuple of (query_string, parameters)
        """
        # Initialize parameters
        params = {
            "query": query,
            "limit": top_k
        }
        
        # Start building the query
        match_clauses = []
        where_clauses = []
        
        # Base match clause for chunks and documents
        match_clauses.append("MATCH (chunk:Chunk)-[:HAS_CHUNK]-(document:Document)")
        
        # Add PMQA reference if provided
        if pmqa_reference:
            if "criteria_id" in pmqa_reference:
                match_clauses.append("MATCH (chunk)-[:RELATES_TO]->(criteria:Criteria)")
                where_clauses.append("criteria.id = $criteriaId")
                params["criteriaId"] = pmqa_reference["criteria_id"]
            elif "subcategory_id" in pmqa_reference:
                match_clauses.append("MATCH (chunk)-[:RELATES_TO]->(subcategory:Subcategory)")
                where_clauses.append("subcategory.id = $subcategoryId")
                params["subcategoryId"] = pmqa_reference["subcategory_id"]
            elif "category_id" in pmqa_reference:
                match_clauses.append("MATCH (chunk)-[:RELATES_TO]->(category:Category)")
                where_clauses.append("category.id = $categoryId")
                params["categoryId"] = pmqa_reference["category_id"]
        
        # Add filters if provided
        if filters:
            if "category" in filters:
                where_clauses.append("document.category = $category")
                params["category"] = filters["category"]
            if "published_after" in filters:
                where_clauses.append("document.published_date >= $publishedAfter")
                params["publishedAfter"] = filters["published_after"]
            if "published_before" in filters:
                where_clauses.append("document.published_date <= $publishedBefore")
                params["publishedBefore"] = filters["published_before"]
            if "author" in filters:
                where_clauses.append("document.author = $author")
                params["author"] = filters["author"]
        
        # Add text search
        where_clauses.append("chunk.content CONTAINS $query OR document.title CONTAINS $query")
        
        # Get PMQA references
        with_clause = """
        OPTIONAL MATCH (chunk)-[:RELATES_TO]->(pmqa)
        WHERE pmqa:Category OR pmqa:Subcategory OR pmqa:Criteria
        WITH document, chunk, collect(pmqa) as pmqaRefs,
        CASE
            WHEN chunk.content CONTAINS $query THEN 3
            WHEN document.title CONTAINS $query THEN 2
            ELSE 1
        END as score
        """
        
        # Build full query
        query_string = f"""
        {' '.join(match_clauses)}
        {' AND '.join(['WHERE ' + clause for clause in where_clauses]) if where_clauses else ''}
        {with_clause}
        RETURN document, chunk, pmqaRefs, score
        ORDER BY score DESC
        LIMIT $limit
        """
        
        return query_string, params

    def _combine_results(
        self, 
        vector_results: List[Dict[str, Any]],
        graph_results: List[Dict[str, Any]],
        vector_weight: float,
        graph_weight: float,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Combine and re-rank results from vector and graph search.
        
        Args:
            vector_results: Results from vector search
            graph_results: Results from graph search
            vector_weight: Weight for vector search results (0-1)
            graph_weight: Weight for graph search results (0-1)
            top_k: Number of top results to return
            
        Returns:
            Combined and re-ranked results
        """
        # Normalize weights
        total_weight = vector_weight + graph_weight
        if total_weight == 0:
            return []
            
        vector_weight = vector_weight / total_weight
        graph_weight = graph_weight / total_weight
        
        # Create a dictionary to combine results by chunk_id
        combined_dict = {}
        
        # Add vector results
        for result in vector_results:
            chunk_id = result["chunk_id"]
            if chunk_id in combined_dict:
                # Update existing entry
                combined_dict[chunk_id]["vector_score"] = result["score"]
                combined_dict[chunk_id]["combined_score"] += result["score"] * vector_weight
            else:
                # Create new entry
                result["vector_score"] = result["score"]
                result["graph_score"] = 0.0
                result["combined_score"] = result["score"] * vector_weight
                combined_dict[chunk_id] = result
        
        # Add graph results
        for result in graph_results:
            chunk_id = result["chunk_id"]
            if chunk_id in combined_dict:
                # Update existing entry
                combined_dict[chunk_id]["graph_score"] = result["score"]
                combined_dict[chunk_id]["combined_score"] += result["score"] * graph_weight
                
                # Merge PMQA references if needed
                existing_refs = {
                    (ref.get("category_id", ""), ref.get("subcategory_id", ""), ref.get("criteria_id", ""))
                    for ref in combined_dict[chunk_id]["pmqa_references"]
                }
                
                for ref in result["pmqa_references"]:
                    ref_tuple = (ref.get("category_id", ""), ref.get("subcategory_id", ""), ref.get("criteria_id", ""))
                    if ref_tuple not in existing_refs:
                        combined_dict[chunk_id]["pmqa_references"].append(ref)
            else:
                # Create new entry
                result["vector_score"] = 0.0
                result["graph_score"] = result["score"]
                result["combined_score"] = result["score"] * graph_weight
                combined_dict[chunk_id] = result
        
        # Convert dictionary back to list and sort by combined score
        combined_results = list(combined_dict.values())
        combined_results.sort(key=lambda x: x["combined_score"], reverse=True)
        
        # Update the score field to be the combined score
        for result in combined_results:
            result["score"] = result["combined_score"]
        
        # Return top k results
        return combined_results[:top_k]


# Create a singleton instance
graph_rag = GraphRAGService()
