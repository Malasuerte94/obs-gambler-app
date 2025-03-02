import logging
from utils.api_client import APIClient

logger = logging.getLogger('APIPoints')

STREAMER_ID = 1
DEFAULT_POINTS = 1


def award_points(user_ids, points=DEFAULT_POINTS, streamer_id=STREAMER_ID):
    if not user_ids:
        logger.info("No users to award points")
        return False

    data = {
        "streamer_id": streamer_id,
        "users": user_ids,
        "points": points
    }

    logger.info(f"Awarding {points} points to {len(user_ids)} users")

    try:
        endpoint = "add-users-points"

        # Use the json parameter instead of data
        import requests
        response = requests.post(
            f"{APIClient.BASE_URL}{endpoint}",
            json=data,  # Use json parameter to ensure proper JSON formatting
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            result = response.json()
            logger.info(f"Successfully awarded points. Response: {result}")
            return True
        else:
            logger.error(f"Failed to award points. Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"API request error when awarding points: {e}", exc_info=True)
        return False