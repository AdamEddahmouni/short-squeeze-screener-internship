# ──────────────────────────────────────────────────────────────────────
#  Short Squeeze Research Screener  —  Makefile
# ──────────────────────────────────────────────────────────────────────
#  Convenience wrappers around `docker compose` and local dev commands.
#
#  Quick reference:
#      make up         → frozen demo + IB Gateway (default)
#      make up-full    → full LOCAL_FULL mode (screener + live IBKR data)
#      make build      → rebuild screener image
#      make dev        → run directly (no Docker) for rapid iteration
#      make logs       → tail all services
#      make logs-*     → tail a single service (logs-screener, logs-gateway)
#      make down       → stop and remove containers
#      make clean      → down + remove volumes
#      make clean-cache→ remove user-level port cache
#      make ps         → show container status
#      make doctor     → print credential/provider report
# ──────────────────────────────────────────────────────────────────────

.PHONY: help up up-full build dev logs logs-screener logs-gateway
.PHONY: down stop clean clean-cache ps pull doctor doctor-json

# ── Help ──────────────────────────────────────────────────────────────

help: ## Show this help
	@printf "\033[1mShort Squeeze Research Screener — quick commands\033[0m\n"
	@printf "  \033[36mmake up\033[0m         Start frozen-demo + IB Gateway  (\033[33mdocker compose up\033[0m)\n"
	@printf "  \033[36mmake up-full\033[0m    Full LOCAL_FULL mode             (\033[33moverride + HEALTHY wait\033[0m)\n"
	@printf "  \033[36mmake build\033[0m      Rebuild screener image\n"
	@printf "  \033[36mmake dev\033[0m        Run directly (no Docker)\n"
	@printf "  \033[36mmake logs\033[0m       Tail all containers\n"
	@printf "  \033[36mmake logs-screener\033[0m  Tail screener logs\n"
	@printf "  \033[36mmake logs-gateway\033[0m  Tail IB Gateway logs\n"
	@printf "  \033[36mmake down\033[0m       Stop and remove containers\n"
	@printf "  \033[36mmake clean\033[0m      Down + remove named volumes\n"
	@printf "  \033[36mmake clean-cache\033[0m Remove user-level port cache\n"
	@printf "  \033[36mmake ps\033[0m         Show container status\n"
	@printf "  \033[36mmake doctor\033[0m         Print credential/provider report\n"
	@printf "  \033[36mmake doctor-json\033[0m     Print report as JSON via jq\n"
	@printf "\n"

# ── Up — both services (frozen demo + Gateway) ────────────────────────

up: ## Start frozen demo + IB Gateway (no API keys required)
	@printf "\033[32m. Starting screener (frozen demo) + IB Gateway...\033[0m\n"
	docker compose up -d
	@printf "\n  \033[36m->\033[0m Open \033[4mhttp://127.0.0.1:8787/\033[0m\n"
	@printf "  \033[36m->\033[0m Run \033[33mmake logs\033[0m to follow output\n"
	@printf "  \033[36m->\033[0m Run \033[33mmake down\033[0m to stop\n"

# ── Up — full LOCAL_FULL (screener uses live Gateway directly) ────────

up-full: ## Start in full LOCAL_FULL mode (wait for Gateway health)
	@printf "\033[32m. Starting in\033[0m \033[1mLOCAL_FULL\033[0m \033[32mmode with live IBKR data...\033[0m\n"
	docker compose -f docker-compose.yml -f docker-compose.local.yml up -d
	@printf "\n  \033[36m->\033[0m Open \033[4mhttp://127.0.0.1:8787/\033[0m\n"
	@printf "  \033[36m->\033[0m Screener waits for Gateway health check\n"
	@printf "  \033[36m->\033[0m Run \033[33mmake logs\033[0m to watch startup progress\n"

# ── Build ─────────────────────────────────────────────────────────────

build: ## Rebuild the screener image (no cache)
	docker compose build --no-cache
	@printf "\n  \033[32mOK\033[0m Image rebuilt.\n"

# ── Dev (no Docker) ───────────────────────────────────────────────────

dev: ## Run the screener directly (no Docker) for rapid iteration
	@printf "\033[32m. Starting screener directly (no Docker)...\033[0m\n"
	python -m apps.research_screener

# ── Logs ──────────────────────────────────────────────────────────────

logs: ## Tail container logs
	docker compose logs -f

logs-screener: ## Tail only the screener container
	docker compose logs -f screener

logs-gateway: ## Tail only the IB Gateway container
	docker compose logs -f ib-gateway

# ── Lifecycle ─────────────────────────────────────────────────────────

down: ## Stop containers and remove network
	docker compose down
	@printf "\n  \033[32mOK\033[0m Containers stopped and removed.\n"

stop: ## Stop containers without removing them
	docker compose stop
	@printf "\n  \033[32mOK\033[0m Containers stopped.\n"

clean: ## Stop, remove containers, and delete named volumes
	docker compose down -v
	@printf "\n  \033[32mOK\033[0m Containers and volumes removed.\n"

clean-cache: ## Remove the user-level IB Gateway port detection cache
	@rm -f ~/.short-squeeze/ib-gateway-port.json
	@printf "\n  \033[32mOK\033[0m Port cache cleared.\n"

ps: ## Show status of all services
	docker compose ps

pull: ## Pre-pull the IB Gateway image
	docker compose pull ib-gateway
	@printf "\n  \033[32mOK\033[0m ib-gateway image pulled.\n"

# ── Diagnostics ───────────────────────────────────────────────────────

doctor: ## Print credential/provider status report
	python -m apps.research_screener.config doctor

doctor-json: ## Print credential/provider status report as JSON, piped through jq (falls back to json.tool)
	@if command -v jq >/dev/null 2>&1; then \
		python -m apps.research_screener.config doctor --json | jq; \
	else \
		python -m apps.research_screener.config doctor --json | python -m json.tool; \
	fi
