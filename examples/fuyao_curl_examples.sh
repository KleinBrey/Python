#!/usr/bin/env bash
set -euo pipefail

# 同花顺扶摇 REST API curl 案例
#
# 使用：
#   export HITHINK_FINANCE_API_KEY="你的 API Key"
#   bash examples/fuyao_curl_examples.sh snapshot 600519.SH
#   bash examples/fuyao_curl_examples.sh history 000001.SZ 60
#   bash examples/fuyao_curl_examples.sh valuation 600519.SH
#   bash examples/fuyao_curl_examples.sh search 贵州茅台
#   bash examples/fuyao_curl_examples.sh hot

: "${HITHINK_FINANCE_API_KEY:?请先 export HITHINK_FINANCE_API_KEY=\"你的 API Key\"}"

FUYAO_BASE_URL="${HITHINK_FINANCE_BASE_URL:-https://fuyao.aicubes.cn}"
API_NAME="${1:-snapshot}"
SYMBOL_OR_QUERY="${2:-600519.SH}"
DAYS="${3:-30}"

fuyao_get() {
  local path="$1"
  shift
  curl \
    --fail-with-body \
    --silent \
    --show-error \
    --get \
    "${FUYAO_BASE_URL}${path}" \
    --header "X-api-key: ${HITHINK_FINANCE_API_KEY}" \
    --header "Accept: application/json" \
    "$@"
}

case "${API_NAME}" in
  snapshot)
    # 最新行情快照；thscodes 支持逗号分隔多个代码。
    fuyao_get \
      "/api/a-share/prices/snapshot" \
      --data-urlencode "thscodes=${SYMBOL_OR_QUERY}"
    ;;

  history)
    # 历史 K 线当前每次只接受一个 thscode，时间参数为 Unix 毫秒。
    END_MS="$(($(date +%s) * 1000))"
    START_MS="$((END_MS - DAYS * 86400000))"
    fuyao_get \
      "/api/a-share/prices/historical" \
      --data-urlencode "thscode=${SYMBOL_OR_QUERY}" \
      --data-urlencode "interval=1d" \
      --data-urlencode "start=${START_MS}" \
      --data-urlencode "end=${END_MS}" \
      --data-urlencode "adjust=forward" \
      --data-urlencode "offset=0"
    ;;

  valuation)
    # 最新估值；thscodes 支持逗号分隔多个代码。
    fuyao_get \
      "/api/a-share/valuations/snapshot" \
      --data-urlencode "thscodes=${SYMBOL_OR_QUERY}"
    ;;

  search)
    # 支持代码、thscode 和中文名称检索。
    fuyao_get \
      "/api/meta/tickers/search" \
      --data-urlencode "q=${SYMBOL_OR_QUERY}" \
      --data-urlencode "asset_type=a-share" \
      --data-urlencode "limit=10"
    ;;

  hot)
    # period=day 为 24 小时热股榜，hour 为小时榜。
    fuyao_get \
      "/api/a-share/special-data/hot-stock-list" \
      --data-urlencode "period=day"
    ;;

  *)
    echo "不支持的案例：${API_NAME}" >&2
    echo "可选值：snapshot、history、valuation、search、hot" >&2
    exit 2
    ;;
esac

echo
