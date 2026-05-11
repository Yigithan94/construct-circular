import logging
import traceback

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting Flask application initialization...")
    from app import app
    logger.info("Flask application imported successfully")
    
    # Debug: Print all registered routes
    @app.route('/debug/routes')
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "url": str(rule),
                "endpoint": rule.endpoint,
                "methods": list(rule.methods)
            })
        return {"routes": routes}
    
    if __name__ == "__main__":
        logger.info("Starting Flask server on port 5000...")
        app.run(host="0.0.0.0", port=5000, debug=True)
except Exception as e:
    logger.error(f"Error during startup: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise