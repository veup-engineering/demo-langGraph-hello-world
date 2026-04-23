from dataclasses import asdict

from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import data
from .serializers import ArticleSerializer, ProductSerializer


@api_view(["GET"])
def list_articles(request):
    """Return all knowledge-base articles, optionally filtered by ?category="""
    category = request.query_params.get("category")
    items = data.KNOWLEDGE_BASE
    if category:
        items = [a for a in items if a.category == category]
    serializer = ArticleSerializer([asdict(a) for a in items], many=True)
    return Response(serializer.data)


@api_view(["GET"])
def search_articles(request):
    """Search knowledge base by ?q=..."""
    q = request.query_params.get("q", "")
    items = data.search_articles(q)
    serializer = ArticleSerializer([asdict(a) for a in items], many=True)
    return Response({"query": q, "count": len(items), "results": serializer.data})


@api_view(["GET"])
def list_products(request):
    """Return all products, optionally filtered by ?category="""
    category = request.query_params.get("category")
    items = data.PRODUCTS
    if category:
        items = [p for p in items if p.category == category]
    serializer = ProductSerializer([asdict(p) for p in items], many=True)
    return Response(serializer.data)


@api_view(["GET"])
def search_products(request):
    """Search products by ?q=..."""
    q = request.query_params.get("q", "")
    items = data.search_products(q)
    serializer = ProductSerializer([asdict(p) for p in items], many=True)
    return Response({"query": q, "count": len(items), "results": serializer.data})
