# import base64
# import json
# import logging

# import discord
# from discord.ext import commands, tasks
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

# from bot.helpers import tools

# logger = logging.getLogger(__name__)
# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


# class Mail(commands.Cog, name="mail"):
#     creds = Credentials.from_authorized_user_file('env/token.json', SCOPES)

#     def __init__(self, bot: commands.Bot):
#         self.bot = bot
#         self.email_query_task.start()

#     async def email_query(self):
#         new_msg_ids = self.check_for_new_mail()
#         embeds = self.parse_new_mail(new_msg_ids)
#         channel = self.bot.get_guild(403364109409845248).get_channel(619565652151238705)
#         for embed in embeds:
#             await channel.send(embed=embed)


#     @commands.command()
#     @commands.is_owner()
#     async def teq(self, ctx: commands.Context, id: str = None):
#         await self.email_query()

#     @tasks.loop(minutes=5.0)
#     async def email_query_task(self):
#         await self.email_query()


#     def check_for_new_mail(self) -> list[str]:
#         """Checks Gmail servers for new mail through the Gmail API.

#         Returns:
#             a list of new message IDs
#         """
#         with open("messages.json", "r") as f:
#             existing_messages = json.load(f)

#         try:
#             service = build('gmail', 'v1', credentials=self.creds)
#             results = service.users().messages().list(userId="me").execute()
#             messages = results.get("messages", [])
#             if not messages:
#                 logger.error("No messages found.")
#             # https://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.users.messages.html#list
#         except HttpError as error:
#             logger.exception("An API error occurred.")

#         with open("messages.json", "w") as f:
#             json.dump(messages, f)

#         new_messages = [group["id"] for group in messages if group["id"] not in [group["id"] for group in existing_messages]]
#         return new_messages

#     def parse_new_mail(self, message_ids: list[str]):
#         embeds = []
#         for message_id in message_ids:
#             try:
#                 service = build('gmail', 'v1', credentials=self.creds)
#                 results = service.users().messages().get(userId="me", id=message_id, format="full").execute()
#                 payload = results["payload"]
#                 # https://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.users.messages.html#get
#             except Exception as e:
#                 print(e)
#                 return
#             with open(f"{message_id}.json", "w") as f:
#                 json.dump(payload, f)
#             # print(json.dumps(payload))
#             content = payload.get("body", []).get("data", "")
#             if content:
#                 cleaned_content = str(base64.urlsafe_b64decode(content), "utf-8")
#             else:
#                 content = []
#                 for part in payload.get("parts", []):
#                     content += [part.get("body", []).get("data")]
#                 # print(content)
#                 cleaned_content = "\n".join([str(base64.urlsafe_b64decode(c), "utf-8") for c in content])

#             embed = tools.create_embed("New Message", cleaned_content)
#             for header in payload.get("headers", []):
#                 if header.get('name') == "From":
#                     name = header.get("value")
#                     embed.set_author(name=name)

#             embeds += [embed]
#         return embeds


# async def setup(bot: commands.Bot) -> None:
#     await bot.add_cog(Mail(bot))
