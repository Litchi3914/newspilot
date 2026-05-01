import type { ReviewRequest, ReviewResponse } from "../types/review";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function reviewArticle(payload: ReviewRequest): Promise<ReviewResponse> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), 250000);

  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/review`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        source: "web",
        review_mode: "standard",
        options: {
          retriever: payload.options?.retriever ?? "bm25",
          llm_provider: payload.options?.llm_provider ?? "openai",
          enable_retrieval: payload.options?.enable_retrieval ?? true,
          enable_llm: payload.options?.enable_llm ?? true,
          enable_diff: payload.options?.enable_diff ?? true
        },
        ...payload
      }),
      signal: controller.signal
    });

    const data = (await res.json()) as ReviewResponse;
    return data;
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      return {
        request_id: "",
        status: "error",
        data: null,
        error: {
          code: "FRONTEND_TIMEOUT",
          message: "审稿耗时较长，请稍后重试或缩短稿件内容。"
        },
        meta: {
          api_version: "v1"
        }
      };
    }

    return {
      request_id: "",
      status: "error",
      data: null,
      error: {
        code: "NETWORK_ERROR",
        message: "网络异常，请检查后端服务是否启动。"
      },
      meta: {
        api_version: "v1"
      }
    };
  } finally {
    window.clearTimeout(timeoutId);
  }
}


