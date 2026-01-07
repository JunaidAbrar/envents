.PHONY: help check-deploy verify clean

help:
	@echo "Envents Django Project - Make Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make check-deploy    Run Django deployment checklist"
	@echo "  make verify          Verify production configuration"
	@echo "  make clean           Clean Python cache files"

check-deploy:
	@echo "Running Django deployment security checklist..."
	@echo "NOTE: Set required environment variables before running this command."
	python manage.py check --deploy --settings=envents_project.settings.production

verify: check-deploy
	@echo ""
	@echo "✅ Production configuration verified!"
	@echo ""
	@echo "Required Railway Environment Variables:"
	@echo "  - SECRET_KEY"
	@echo "  - DATABASE_URL"
	@echo "  - AWS_ACCESS_KEY_ID"
	@echo "  - AWS_SECRET_ACCESS_KEY"
	@echo "  - AWS_STORAGE_BUCKET_NAME"
	@echo "  - EMAIL_BACKEND, EMAIL_HOST, EMAIL_PORT, etc."
	@echo ""
	@echo "See README.md for complete deployment guide."

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	@echo "✅ Cleaned Python cache files"
