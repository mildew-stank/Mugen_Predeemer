import requests
import logging


class Predeemer:
    def __init__(self, client_id, access_token):
        self.client_id = client_id
        self.access_token = access_token
        self.user_id = self.get_user_id_from_access_token()
        logging.basicConfig(
            filename="cache/error.log",
            format="%(asctime)s %(levelname)-8s %(message)s",
            level=logging.DEBUG,
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def get_user_id_from_access_token(self):
        headers = {
            "Authorization": "Bearer " + str(self.access_token),
            "Client-Id": str(self.client_id),  # this is the registered api app id
        }

        try:
            response = requests.get("https://api.twitch.tv/helix/users", headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            logging.debug(error)
            raise Exception("Error occured while attempting to access users")

        data = response.json()

        return data["data"][0]["id"]

    def create_custom_reward(self, title, cost, prompt="", is_max_per_stream_enabled=False, max_per_stream=10, is_max_per_user_per_stream_enabled=False):
        headers = {
            'client-id': str(self.user_id),
            'Authorization': "Bearer " + str(self.access_token),
            'Content-Type': 'application/json',
        }
        
        params = {
            'broadcaster_id': str(self.user_id),
        }
        
        json_data = {
            'title': str(title),
            'cost': str(cost),
            'is_max_per_stream_enabled': str(is_max_per_stream_enabled),
            'max_per_stream': str(max_per_stream),
            'is_max_per_user_per_stream_enabled': str(is_max_per_user_per_stream_enabled),
            'max_per_user_per_stream': '1',
            "is_user_input_required": True,
            "prompt": str(prompt),
        }
        
        try:
            response = requests.post(
                'https://api.twitch.tv/helix/channel_points/custom_rewards',
                params=params,
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            logging.debug(error)
            raise Exception("Error occured while attempting to create reward")

        data = response.json()

        return data["data"][0]["id"]

    def update_custom_reward(self, reward_id, cost, is_max_per_stream_enabled=False, max_per_stream=10, is_max_per_user_per_stream_enabled=False):
        headers = {
            'client-id': str(self.client_id),
            'Authorization': "Bearer " + str(self.access_token),
            'Content-Type': 'application/json',
        }
        
        params = {
            'broadcaster_id': str(self.user_id),
            'id': str(reward_id),
        }
        
        json_data = {
            'cost': str(cost),
            'is_max_per_stream_enabled': str(is_max_per_stream_enabled),
            'max_per_stream': str(max_per_stream),
            'is_max_per_user_per_stream_enabled': str(is_max_per_user_per_stream_enabled),
            'max_per_user_per_stream': '1',
        }
        
        try:
            response = requests.patch(
                'https://api.twitch.tv/helix/channel_points/custom_rewards',
                params=params,
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            logging.debug(error)
            raise Exception("Error occured while attempting to update reward")

    def delete_custom_reward(self, reward_id):  # TODO: make this try_delete... and return true or false. also make display_error take the string as an arg and add option to work better with a gui
        headers = {
            'Client-Id': str(self.client_id),
            'Authorization': "Bearer " + str(self.access_token),
        }
        
        params = {
            'broadcaster_id': str(self.user_id),
            'id': str(reward_id),
        }
        
        try:
            response = requests.delete('https://api.twitch.tv/helix/channel_points/custom_rewards', params=params, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            raise Exception("Error occured while attempting to delete reward: {error}")

    def get_custom_reward_redemptions(self, reward_id):
        headers = {
            'client-id': str(self.client_id),
            'Authorization': "Bearer " + str(self.access_token),
        }
        
        params = {
            'broadcaster_id': str(self.user_id),
            'reward_id': str(reward_id),
            'status': 'UNFULFILLED',
            "first": "50"  # TODO: make method recursive with pagination for unlimited rewards
        }
        
        try:
            response = requests.get('https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions', params=params, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            logging.debug(error)
            raise Exception("Error occured while attempting to redeem reward")

        data = response.json()

        return data

    def update_redemption_status(self, reward_id, redemption_id, status):
        headers = {
            'client-id': str(self.client_id),
            'Authorization': "Bearer " + str(self.access_token),
            'Content-Type': 'application/json',
        }
        
        params = {
            'broadcaster_id': str(self.user_id),
            'reward_id': str(reward_id),
            'id': str(redemption_id),
        }
        
        json_data = {
            'status': str(status),
        }
        
        try:
            response = requests.patch(
                'https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions',
                params=params,
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            logging.debug(error)
            raise Exception("Error occured while attempting to refund reward")

    def create_prediction(self, title, outcomes, timer=30):
        headers = {
            'Client-Id': str(self.client_id),
            'Authorization': "Bearer " + str(self.access_token),
            'Content-Type': 'application/json',
        }
        
        json_data = {
            'broadcaster_id': str(self.user_id),
            'title': str(title),
            'outcomes': [  # TODO: this is purpose built in accepting only two outcomes, but it would be better to have it completely generic in the future
                {
                    'title': str(outcomes[0]),
                },
                {
                    'title': str(outcomes[1]),
                },
            ],
            'prediction_window': str(timer),
        }

        try:
            response = requests.post('https://api.twitch.tv/helix/predictions', headers=headers, json=json_data)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            logging.debug(error)
            raise Exception("Error occured while attempting to create prediction")

        data = response.json()

        return data["data"][0]["outcomes"]  # from this you can do [0 OR 1]["id" OR ["title"]] and use id for end_prediction winning_outcome_id

    def end_prediction(self, prediction_id, status, winning_outcome_id):  # status should be "RESOLVED" to call it, "CANCELED" to refund it
        headers = {
            'Client-Id': str(self.client_id),
            'Authorization': "Bearer " + str(self.access_token),
            'Content-Type': 'application/json',
        }
        
        json_data = {
            'broadcaster_id': str(self.user_id),
            'id': str(prediction_id),
            'status': str(status),
            'winning_outcome_id': str(winning_outcome_id),
        }

        try:
            response = requests.patch('https://api.twitch.tv/helix/predictions', headers=headers, json=json_data)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            logging.debug(error)
            raise Exception("Error occured while attempting to end prediction")

    def display_error(self, error):
        print(error)
        input()
        raise SystemExit()