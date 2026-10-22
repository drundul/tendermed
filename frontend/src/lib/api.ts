/**
 * TenderMed API Client
 * Взаимодействие Next.js фронтенда с FastAPI бэкендом.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("tendermed_token");
}

export function setToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("tendermed_token", token);
  }
}

export function removeToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("tendermed_token");
  }
}

export function getOpenAIKey(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("tendermed_openai_key") || "";
}

export function setOpenAIKey(key: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("tendermed_openai_key", key.trim());
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const userOpenAIKey = getOpenAIKey();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (userOpenAIKey && !headers["X-OpenAI-Key"]) {
    headers["X-OpenAI-Key"] = userOpenAIKey;
  }

  // Не устанавливаем Content-Type для FormData
  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorDetail = "Произошла ошибка при обращении к серверу";
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || errorDetail;
    } catch {
      // Игнорируем ошибку парсинга JSON
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  auth: {
    async register(payload: { email: string; password: string; company_name?: string }) {
      const data = await request<{ access_token: string; available_credits: number; email: string }>(
        "/api/auth/register",
        {
          method: "POST",
          body: JSON.stringify(payload),
        }
      );
      setToken(data.access_token);
      return data;
    },

    async login(payload: { email: string; password: string }) {
      const data = await request<{ access_token: string; available_credits: number; email: string }>(
        "/api/auth/login",
        {
          method: "POST",
          body: JSON.stringify(payload),
        }
      );
      setToken(data.access_token);
      return data;
    },

    async getMe() {
      return request<{
        id: number;
        email: string;
        company_name?: string;
        available_credits: number;
        is_active: boolean;
      }>("/api/auth/me");
    },

    logout() {
      removeToken();
    },
  },

  tenders: {
    async analyzeUrl(url: string, modelName: string = "gpt-5.4-mini", demoMode: boolean = false, apiKey?: string) {
      const effectiveKey = apiKey || getOpenAIKey();
      return request<{
        audit_id: number;
        report: any;
        execution_time_seconds: number;
        total_documents: number;
        anonymization_stats: any;
        remaining_credits: number;
      }>("/api/tenders/analyze-url", {
        method: "POST",
        body: JSON.stringify({
          url,
          model_name: modelName,
          demo_mode: demoMode,
          api_key: effectiveKey || undefined,
        }),
      });
    },

    async analyzeFiles(files: File[], modelName: string = "gpt-5.4-mini", demoMode: boolean = false, apiKey?: string) {
      const effectiveKey = apiKey || getOpenAIKey();
      const formData = new FormData();
      for (const file of files) {
        formData.append("files", file);
      }
      formData.append("model_name", modelName);
      formData.append("demo_mode", String(demoMode));

      const headers: Record<string, string> = {};
      if (effectiveKey) {
        headers["X-OpenAI-Key"] = effectiveKey;
      }

      return request<{
        audit_id: number;
        report: any;
        execution_time_seconds: number;
        total_documents: number;
        anonymization_stats: any;
        remaining_credits: number;
      }>("/api/tenders/analyze-files", {
        method: "POST",
        body: formData,
        headers,
      });
    },

    async getHistory() {
      return request<
        Array<{
          id: number;
          notice_number?: string;
          purchase_subject: string;
          customer_name?: string;
          law_type: string;
          verdict: string;
          risk_score: number;
          created_at: string;
        }>
      >("/api/tenders/history");
    },

    async getDetail(auditId: number) {
      return request<{
        id: number;
        notice_number?: string;
        source_url?: string;
        created_at: string;
        report: any;
      }>(`/api/tenders/${auditId}`);
    },
  },

  exports: {
    async downloadFile(endpoint: string, defaultFilename: string) {
      const token = getToken();
      const headers: Record<string, string> = {};
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const res = await fetch(`${API_BASE_URL}${endpoint}`, { headers });
      if (!res.ok) {
        throw new Error("Не удалось скачать файл");
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = defaultFilename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    },

    async downloadReportDocx(auditId: number, noticeNumber?: string) {
      const filename = `Tender_Audit_${noticeNumber || "Report"}.docx`;
      return this.downloadFile(`/api/exports/tenders/${auditId}/report.docx`, filename);
    },

    async downloadClarificationsDocx(auditId: number, noticeNumber?: string) {
      const filename = `Vse_Zaprosy_${noticeNumber || "44FZ"}.docx`;
      return this.downloadFile(`/api/exports/tenders/${auditId}/clarifications.docx`, filename);
    },

    async downloadSingleClarificationDocx(auditId: number, index: number, noticeNumber?: string) {
      const filename = `Zapros_Raziasneniy_${index}_${noticeNumber || "44FZ"}.docx`;
      return this.downloadFile(`/api/exports/tenders/${auditId}/clarification/${index}.docx`, filename);
    },

    async downloadFasComplaintDocx(auditId: number, noticeNumber?: string) {
      const filename = `Zhaloba_FAS_${noticeNumber || "44FZ"}.docx`;
      return this.downloadFile(`/api/exports/tenders/${auditId}/fas-complaint.docx`, filename);
    },

    async downloadReportMd(auditId: number, noticeNumber?: string) {
      const filename = `Tender_Audit_${noticeNumber || "Report"}.md`;
      return this.downloadFile(`/api/exports/tenders/${auditId}/report.md`, filename);
    },
  },

  billing: {
    async getPlans() {
      return request<{
        plans: Array<{
          id: string;
          name: string;
          price_rub: number;
          credits: number;
          price_per_audit: number;
          description: string;
          features: string[];
          is_popular?: boolean;
        }>;
      }>("/api/billing/plans");
    },

    async checkout(planId: string) {
      return request<{
        success: boolean;
        message: string;
        added_credits: number;
        new_total_credits: number;
        transaction_id: number;
      }>("/api/billing/checkout", {
        method: "POST",
        body: JSON.stringify({ plan_id: planId }),
      });
    },

    async getTransactions() {
      return request<
        Array<{
          id: number;
          plan_id: string;
          amount_rub: number;
          credits_added: number;
          status: string;
          created_at: string;
        }>
      >("/api/billing/transactions");
    },
  },
};
