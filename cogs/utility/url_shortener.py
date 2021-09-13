import discord
from discord.ext import commands
import requests


def shortner(url: str) -> str:
    """
    returns shortened link

    :param url: link to shorten
    :type url: str
    :return: shortened link
    :rtype: str
    """
    with requests.get(
        f"https://cutt.ly/api/api.php?key=18e866ec48230e692db0f4a225c72fcabfb1e&short={url}"
    ) as response:
        return f"{response.json()['url']['shortLink']}"


class UrlShortener(commands.Cog):
    "Command for shortening urls"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Shrinks url")
    async def shrink(self, ctx, full_url: str) -> None:
        """
        created shortened links

        :param full_url: link to shorten
        :type full_url: str
        """
        await ctx.send(f"shortend link:\n {shortner(full_url)}")


def setup(bot):
    bot.add_cog(UrlShortener(bot))
