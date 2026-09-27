export type RegisterRequest = {
    email: string;
    password: string;
    name?: string | null;
  };
  
  export type RegisterResponse = {
    message: string;
    user: {
      id: number;
      email: string;
      name: string | null;
      created_at: string;
      last_login_at: string | null;
    };
  };
  
  export type LoginRequest = {
    email: string;
    password: string;
  };
  
  export type LoginResponse = {
    message: string;
    access_token: string;
    token_type: string;
    user: {
      id: number;
      email: string;
      name: string | null;
    };
  };
  
  function getApiBaseUrl(): string {
    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:18080";
  
    return baseUrl.replace(/\/+$/, "");
  }
  
  async function request<T>(
    path: string,
    options?: RequestInit
  ): Promise<T> {
    const response = await fetch(`${getApiBaseUrl()}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers ?? {}),
      },
    });
  
    if (!response.ok) {
      const error = await response.json().catch(() => null);
  
      throw new Error(
        error?.detail ||
          `API ${path} thất bại: ${response.status} ${response.statusText}`
      );
    }
  
    return response.json() as Promise<T>;
  }
  
  /**
   * Đăng ký tài khoản.
   *
   * Backend:
   * POST /auth/register
   */
  export async function register(
    data: RegisterRequest
  ): Promise<RegisterResponse> {
    return request<RegisterResponse>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }
  
  /**
   * Đăng nhập tài khoản.
   *
   * Backend:
   * POST /auth/login
   */
  export async function login(
    data: LoginRequest
  ): Promise<LoginResponse> {
    return request<LoginResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }