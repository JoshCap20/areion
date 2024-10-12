from areion import (
    AreionServerBuilder,
    DefaultRouter,
    HttpRequest,
    HttpResponse,
    create_json_response
)
from typing import List, Optional

# Sample data: List of items (e.g., products)
items = [
    {'id': 1, 'name': 'Apple iPhone 13', 'category': 'Electronics', 'price': 999},
    {'id': 2, 'name': 'Samsung Galaxy S21', 'category': 'Electronics', 'price': 799},
    {'id': 3, 'name': 'Dell XPS 13', 'category': 'Computers', 'price': 1199},
    {'id': 4, 'name': 'Apple MacBook Pro', 'category': 'Computers', 'price': 1299},
    {'id': 5, 'name': 'Sony WH-1000XM4', 'category': 'Audio', 'price': 349},
]

# Initialize the router
router = DefaultRouter()

@router.route("/search", methods=["GET"])
def search_items(
    request: HttpRequest,
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = 'name',
    sort_order: Optional[str] = 'asc',
    page: Optional[int] = 1,
    page_size: Optional[int] = 10
):
    """
    Searches for items based on query parameters.

    Parameters:
        query (str): Keyword to search in item names.
        category (str): Filter by item category.
        min_price (float): Minimum price filter.
        max_price (float): Maximum price filter.
        sort_by (str): Field to sort by (e.g., 'name', 'price').
        sort_order (str): Sort order ('asc' or 'desc').
        page (int): Page number for pagination.
        page_size (int): Number of items per page.

    Returns:
        200: A paginated list of items matching the search criteria.
    """
    # Parse query parameters
    query_params = request.get_parsed_query_params()

    # Get and validate parameters
    query = query_params.get('query', query)
    category = query_params.get('category', category)
    min_price = float(query_params.get('min_price', min_price or 0))
    max_price = float(query_params.get('max_price', max_price or float('inf')))
    sort_by = query_params.get('sort_by', sort_by)
    sort_order = query_params.get('sort_order', sort_order)
    page = int(query_params.get('page', page))
    page_size = int(query_params.get('page_size', page_size))

    # Filter items based on query parameters
    filtered_items = items

    if query:
        filtered_items = [
            item for item in filtered_items
            if query.lower() in item['name'].lower()
        ]

    if category:
        filtered_items = [
            item for item in filtered_items
            if item['category'].lower() == category.lower()
        ]

    filtered_items = [
        item for item in filtered_items
        if min_price <= item['price'] <= max_price
    ]

    # Sort items
    reverse_order = sort_order.lower() == 'desc'
    filtered_items.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse_order)

    # Pagination
    total_items = len(filtered_items)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_items = filtered_items[start_index:end_index]

    # Prepare response
    response_data = {
        'total_items': total_items,
        'page': page,
        'page_size': page_size,
        'items': paginated_items
    }

    return create_json_response(response_data)

server = (
    AreionServerBuilder()
    .with_router(router)
    .with_development_mode(True)  # Enables Swagger UI and OpenAPI routes
    .build()
)

if __name__ == "__main__":
    server.run()
