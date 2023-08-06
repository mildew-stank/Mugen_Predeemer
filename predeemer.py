import requests
import logging


class Predeemer:
    def __init__(self, client_id, access_token):
        logging.basicConfig(
            filename="cache/error.log",
            format="%(asctime)s %(levelname)-8s %(message)s",
            level=logging.DEBUG,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.client_id = client_id
        self.access_token = access_token
        self.user_id = self.get_user_id_from_access_token()

    def get_user_id_from_access_token(self):
        headers = {
            "Authorization": "Bearer " + str(self.access_token),
            "Client-Id": str(self.client_id),  # this is the registered api app id
        }

        try:
            response = requests.get("https://api.twitch.tv/helix/users", headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            self.handle_error("Error occured while attempting to create reward", error)

        data = response.json()

        return data["data"][0]["id"]

    def create_custom_reward(
        self,
        title,
        cost,
        prompt="",
        is_max_per_stream_enabled=False,
        max_per_stream=10,
        is_max_per_user_per_stream_enabled=False,
    ):
        headers = {
            "client-id": str(self.user_id),
            "Authorization": "Bearer " + str(self.access_token),
            "Content-Type": "application/json",
        }

        params = {
            "broadcaster_id": str(self.user_id),
        }

        json_data = {
            "title": title,
            "cost": cost,
            "is_max_per_stream_enabled": is_max_per_stream_enabled,
            "max_per_stream": max_per_stream,
            "is_max_per_user_per_stream_enabled": is_max_per_user_per_stream_enabled,
            "max_per_user_per_stream": "1",
            "is_user_input_required": True,
            "prompt": prompt,
        }

        try:
            response = requests.post(
                "https://api.twitch.tv/helix/channel_points/custom_rewards",
                params=params,
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            self.handle_error("Error occured while attempting to create reward", error)

        data = response.json()

        return data["data"][0]["id"]

    def update_custom_reward(self, reward_id, cost, is_max_per_stream_enabled=False, max_per_stream=10, is_max_per_user_per_stream_enabled=False):
        headers = {
            "client-id": str(self.client_id),
            "Authorization": "Bearer " + str(self.access_token),
            "Content-Type": "application/json",
        }

        params = {
            "broadcaster_id": str(self.user_id),
            "id": str(reward_id),
        }

        json_data = {
            "cost": cost,
            "is_max_per_stream_enabled": is_max_per_stream_enabled,
            "max_per_stream": max_per_stream,
            "is_max_per_user_per_stream_enabled": is_max_per_user_per_stream_enabled,
            "max_per_user_per_stream": "1",
        }

        try:
            response = requests.patch(
                "https://api.twitch.tv/helix/channel_points/custom_rewards",
                params=params,
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            self.handle_error("Error occured while attempting to update reward", error)

    def delete_custom_reward(self, reward_id):
        headers = {
            "Client-Id": str(self.client_id),
            "Authorization": "Bearer " + str(self.access_token),
        }

        params = {
            "broadcaster_id": str(self.user_id),
            "id": str(reward_id),
        }

        try:
            response = requests.delete(
                "https://api.twitch.tv/helix/channel_points/custom_rewards",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            self.handle_error("Error occured while attempting to delete reward", error)

    def get_custom_reward_redemptions(self, reward_id):
        headers = {
            "client-id": str(self.client_id),
            "Authorization": "Bearer " + str(self.access_token),
        }

        params = {
            "broadcaster_id": str(self.user_id),
            "reward_id": str(reward_id),
            "status": "UNFULFILLED",
            "first": "50",  # TODO: make method recursive with pagination for unlimited rewards
        }

        try:
            response = requests.get(
                "https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            self.handle_error("Error occured while attempting to redeem reward", error)

        data = response.json()

        return data

    def update_redemption_status(self, reward_id, redemption_id, status):
        headers = {
            "client-id": str(self.client_id),
            "Authorization": "Bearer " + str(self.access_token),
            "Content-Type": "application/json",
        }

        params = {
            "broadcaster_id": str(self.user_id),
            "reward_id": str(reward_id),
            "id": str(redemption_id),
        }

        json_data = {
            "status": status,
        }

        try:
            response = requests.patch(
                "https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions",
                params=params,
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            self.handle_error("Error occured while attempting to refund reward", error)

    def create_prediction(self, title, outcomes, timer=30):
        headers = {
            "Client-Id": str(self.client_id),
            "Authorization": "Bearer " + str(self.access_token),
            "Content-Type": "application/json",
        }

        json_data = {
            "broadcaster_id": self.user_id,
            "title": title,
            "outcomes": [{"title": outcomes[0],},
                         {"title": outcomes[1],},
            ],
            "prediction_window": timer,
        }

        try:
            response = requests.post(
                "https://api.twitch.tv/helix/predictions",
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            self.handle_error(
                "Error occured while attempting to create prediction", error
            )

        data = response.json()

        # from this you can do [0 OR 1]["id" OR "title"] and use id for end_prediction winning_outcome_id
        return data["data"][0]["outcomes"]

    def end_prediction(self, prediction_id, status, winning_outcome_id):  # status should be "RESOLVED" to call it, "CANCELED" to refund it
        headers = {
            "Client-Id": str(self.client_id),
            "Authorization": "Bearer " + str(self.access_token),
            "Content-Type": "application/json",
        }

        json_data = {
            "broadcaster_id": self.user_id,
            "id": prediction_id,
            "status": status,
            "winning_outcome_id": winning_outcome_id,
        }

        try:
            response = requests.patch(
                "https://api.twitch.tv/helix/predictions",
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            self.handle_error("Error occured while attempting to end prediction", error)

    def handle_error(self, info, error):
        logging.debug(f"{info}: {error}")
        raise Exception(error)
