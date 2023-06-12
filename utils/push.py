from firebase_admin import messaging

def send_message(token: str, title: str, body: str):
    # registration_token = 'ee_H4TilS2mzOTuf01upcd:APA91bEwv6jhN3JTruCMGvdgQcFErDMcvsz2O0Ncg8J9NzjX1afLDwg9KliQEDVzJ6mNYN49qLViuz6qTT6WezLjao5Dh8a-PIW5vgL1TIYtqXjaNs4ZsmqazTSvUI69Djd5r-Ymwk0X'
    message = messaging.Message(
    notification = messaging.Notification(
        title = title,
        body = body
    ),
    token=token,
    )
    response = messaging.send(message)
    return response