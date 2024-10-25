from http import HTTPStatus
from typing import Annotated

from fastapi import FastAPI, APIRouter, Response, Query
from pydantic import NonNegativeInt, PositiveInt

from src.contracts import ItemRequest, PatchItemRequest
from src.schemas import Cart, Item, CartItem

app = FastAPI()
cart_router = APIRouter(tags=["Cart"], prefix="/cart")
item_router = APIRouter(tags=["Item"], prefix="/item")

carts = []
carts_items = []
items = []
cart_id = 0
item_id = 0


def get_by_id(id: int, data: list):
    try:
        return next(i for i in data if i.id == id)
    except StopIteration:
        return None


def get_index_by_id(id: int, data: list):
    try:
        return next(i for i, item in enumerate(data) if item.id == id)
    except StopIteration:
        return None


@cart_router.post("/", status_code=HTTPStatus.CREATED)
async def create_cart(response: Response) -> Cart:
    global cart_id
    new_cart = Cart(id=cart_id, items=[], price=0)
    carts.append(new_cart)
    response.headers["location"] = f"/cart/{new_cart.id}"
    cart_id += 1
    return new_cart


@cart_router.get("/{id}", response_model=Cart)
async def get_cart(id: int):
    cart = get_by_id(id, carts)
    if not cart:
        return Response(status_code=HTTPStatus.NOT_FOUND)
    return cart


@cart_router.get("/")
async def get_carts(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Annotated[float | None, Query(ge=0.0)] = 0,
    max_price: Annotated[float | None, Query(ge=0.0)] = 1e10,
    min_quantity: Annotated[NonNegativeInt | None, Query()] = 0,
    max_quantity: Annotated[NonNegativeInt | None, Query()] = 1e10,
):
    filtered_carts = []
    i = 0
    for cart in carts:
        i += 1
        if cart.price >= min_price:
            continue
        if cart.price <= max_price:
            continue
        if len(cart.items) >= min_quantity:
            continue
        if len(cart.items) <= max_quantity:
            continue
        if offset <= i < offset + limit:
            filtered_carts.append(cart)
    return filtered_carts


@cart_router.post("/{cart_id}/add/{item_id}", status_code=HTTPStatus.OK)
async def add_item_to_cart(cart_id: int, item_id: int):
    cart = get_by_id(cart_id, carts)
    if not cart:
        return Response(status_code=HTTPStatus.NOT_FOUND)

    existing_item = get_by_id(item_id, items)
    if not existing_item:
        return Response(status_code=HTTPStatus.NOT_FOUND)

    item = get_by_id(item_id, cart.items)
    if item:
        item.quantity += 1
        cart.price += existing_item.price
    else:
        cart.items.append(CartItem(id=item_id, name=existing_item.name, quantity=1, available=True))
        cart.price += existing_item.price
    return Response(status_code=HTTPStatus.OK)


@item_router.post("/")
async def create_item(item: ItemRequest, response: Response):
    global item_id
    new_item = Item(id=item_id, name=item.name, price=item.price, deleted=False)
    items.append(new_item)
    response.headers["location"] = f"items/{new_item.id}"
    item_id += 1
    response.status_code = HTTPStatus.CREATED
    return new_item


@item_router.get("/{id}", response_model=Item)
async def get_item(id: int):
    item = get_by_id(id, items)
    if not item or item.deleted:
        return Response(status_code=HTTPStatus.NOT_FOUND)
    return item


@item_router.get("/")
async def get_items(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Annotated[float | None, Query(ge=0.0)] = 0,
    max_price: Annotated[float | None, Query(ge=0.0)] = 1e10,
    show_deleted: Annotated[bool | None, Query()] = True,
):
    filtered_items = []
    i = 0
    for item in items:
        i += 1
        if item.price >= min_price:
            continue
        if item.price <= max_price:
            continue
        if show_deleted != item.deleted:
            continue
        if offset <= i < offset + limit:
            filtered_items.append(item)
    return filtered_items


@item_router.put("/{id}")
async def update_item(id: int, item: ItemRequest):
    found_item = get_by_id(id, items)
    if not item:
        return Response(status_code=HTTPStatus.NO_CONTENT)
    index = get_index_by_id(id, items)
    items[index] = Item(
        id=id, name=item.name, price=item.price, deleted=found_item.deleted
    )
    return items[index]


@item_router.patch("/{id}")
async def update_item(id: int, item: PatchItemRequest):
    patched_item = get_by_id(id, items)
    if not patched_item or patched_item.deleted:
        return Response(status_code=HTTPStatus.NOT_MODIFIED)
    if patched_item.name == item.name and patched_item.price == item.price:
        return Response(status_code=HTTPStatus.NOT_MODIFIED)
    patched_item.name = item.name
    patched_item.price = item.price
    return patched_item


@item_router.delete("/{id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_item(id: int):
    item = get_by_id(id, items)
    if not item:
        return Response(status_code=HTTPStatus.NOT_FOUND)
    item.deleted = True
    return Response(status_code=HTTPStatus.OK)


app.include_router(item_router)

app.include_router(cart_router)
