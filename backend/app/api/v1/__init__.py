from fastapi import APIRouter

from app.api.v1 import auth, conversations, suppliers, products, inventory, procurement, receipts, invoices

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(products.router, tags=["products"])
api_router.include_router(products.warehouse_router, tags=["warehouses"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(procurement.router, tags=["procurement"])
api_router.include_router(procurement.requisition_router, tags=["requisitions"])
api_router.include_router(receipts.router, tags=["receipts"])
api_router.include_router(invoices.router, tags=["invoices"])