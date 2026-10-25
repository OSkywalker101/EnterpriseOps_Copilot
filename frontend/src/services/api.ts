import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
      const token = localStorage.getItem('access_token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken,
              });
              const { access_token, refresh_token } = response.data;
              localStorage.setItem('access_token', access_token);
              localStorage.setItem('refresh_token', refresh_token);
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              return this.client(originalRequest);
            }
          } catch {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', { email, password });
    return response.data;
  }

  async register(data: { email: string; password: string; full_name: string; role?: string }) {
    const response = await this.client.post('/auth/register', data);
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  async getConversations() {
    const response = await this.client.get('/conversations');
    return response.data;
  }

  async createConversation(title: string) {
    const response = await this.client.post('/conversations', { title });
    return response.data;
  }

  async getConversation(id: number) {
    const response = await this.client.get(`/conversations/${id}`);
    return response.data;
  }

  async deleteConversation(id: number) {
    await this.client.delete(`/conversations/${id}`);
  }

  async sendMessage(message: string, conversationId?: number) {
    const response = await this.client.post(`/conversations/${conversationId || ''}/messages`, { message });
    return response.data;
  }

  async getSuppliers(params?: Record<string, unknown>) {
    const response = await this.client.get('/suppliers', { params });
    return response.data;
  }

  async getSupplier(id: number) {
    const response = await this.client.get(`/suppliers/${id}`);
    return response.data;
  }

  async getProducts(params?: Record<string, unknown>) {
    const response = await this.client.get('/products', { params });
    return response.data;
  }

  async getProduct(id: number) {
    const response = await this.client.get(`/products/${id}`);
    return response.data;
  }

  async getWarehouses() {
    const response = await this.client.get('/warehouses');
    return response.data;
  }

  async getInventoryBalances(params?: Record<string, unknown>) {
    const response = await this.client.get('/inventory/balances', { params });
    return response.data;
  }

  async getLowStock(warehouseId?: number) {
    const response = await this.client.get('/inventory/low-stock', { params: { warehouse_id: warehouseId } });
    return response.data;
  }

  async getInventoryMovements(params?: Record<string, unknown>) {
    const response = await this.client.get('/inventory/movements', { params });
    return response.data;
  }

  async getPurchaseOrders(params?: Record<string, unknown>) {
    const response = await this.client.get('/purchase-orders', { params });
    return response.data;
  }

  async getPurchaseOrder(id: number) {
    const response = await this.client.get(`/purchase-orders/${id}`);
    return response.data;
  }

  async getPendingApprovals() {
    const response = await this.client.get('/purchase-orders/pending-approvals');
    return response.data;
  }

  async getOverdueDeliveries() {
    const response = await this.client.get('/purchase-orders/overdue');
    return response.data;
  }

  async approvePurchaseOrder(id: number, comments?: string) {
    const response = await this.client.post(`/purchase-orders/${id}/approve`, { comments });
    return response.data;
  }

  async rejectPurchaseOrder(id: number, comments: string) {
    const response = await this.client.post(`/purchase-orders/${id}/reject`, { comments });
    return response.data;
  }

  async getGoodsReceipts(params?: Record<string, unknown>) {
    const response = await this.client.get('/goods-receipts', { params });
    return response.data;
  }

  async getGoodsReceipt(id: number) {
    const response = await this.client.get(`/goods-receipts/${id}`);
    return response.data;
  }

  async getInvoices(params?: Record<string, unknown>) {
    const response = await this.client.get('/supplier-invoices', { params });
    return response.data;
  }

  async getInvoice(id: number) {
    const response = await this.client.get(`/supplier-invoices/${id}`);
    return response.data;
  }

  async matchInvoicePO(invoiceId: number) {
    const response = await this.client.post(`/supplier-invoices/${invoiceId}/match-po`);
    return response.data;
  }

  async matchInvoiceGR(invoiceId: number) {
    const response = await this.client.post(`/supplier-invoices/${invoiceId}/match-gr`);
    return response.data;
  }
}

export const api = new ApiClient();