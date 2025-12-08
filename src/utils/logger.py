import logging
import os
from ..core.config import settings

# Create logs directory if it doesn't exist
os.makedirs(settings.logs_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(settings.logs_dir, 'apkscanner.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)