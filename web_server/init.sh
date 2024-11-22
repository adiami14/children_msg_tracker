#!/bin/bash


# ngrok config add-authtoken 2eak3qyS2xeVxiZgZVVkNcXrEkJ_6fr9btKKR7Ky8BwZrQcke
# echo "ngrok config complete" >> /log/web_server.log
# sleep 2
# ngrok http 80 --log=/log/ngrok.log > /dev/null &
# echo "ngrok server is up!" >> /log/web_server.log
# sleep 2
# while true; do
#     export WEBHOOK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r ".tunnels[0].public_url")
#     if [ -n "$WEBHOOK_URL" ]; then
#         echo "sending ngrok url via whatsapp $WEBHOOK_URL" >> /log/web_server.log
#         curl -s "http://web_server.sergei/send_whatsapp?msg='$WEBHOOK_URL'&user='adi'" >> /log/web_server.log

#         break
#     fi
#     sleep 2
# done

# echo "Webhook URL: $WEBHOOK_URL" >> /log/web_server.log

python3 /src/web_server/web_server_api.py -f /log/web_server.log
# tail -f /dev/null
