import logging
from utils.api_client import APIClient

logger = logging.getLogger('APIPoints')

def award_points(user_ids, points, streamer_id, api_client):
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
        response = api_client.post(endpoint, json=data)

        if response and "error" not in response:
            logger.info(f"Successfully awarded points. Response: {response}")
            return True
        else:
            error_message = response.get("error", "Unknown error") if response else "Empty response"
            logger.error(f"Failed to award points. Error: {error_message}")
            return False
    except Exception as e:
        logger.error(f"API request error when awarding points: {e}", exc_info=True)
        return False