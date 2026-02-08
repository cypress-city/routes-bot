import discord
from discord.ext import commands
from random import choice

from modules.core import Bot
from modules.embeds import blue_embed, red_embed
from modules.routes import courses, routes


async def course_autocomplete(inter: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    matches = sorted([g for g in courses.values() if g.closeness(current)], key=lambda c: -c.closeness(current))
    return [discord.app_commands.Choice(name=g.full_display, value=g.name) for g in matches][:25]


class RouteCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="list",
        description="View a list of routes."
    )
    @discord.app_commands.autocomplete(
        from_track=course_autocomplete, to_track=course_autocomplete
    )
    @discord.app_commands.describe(
        from_track="Track name", to_track="Track name"
    )
    @discord.app_commands.rename(
        from_track="from", to_track="to"
    )
    async def list_command(self, inter: discord.Interaction, from_track: str = None, to_track: str = None):
        if not from_track and not to_track:
            by_end_track = {
                g: ", ".join(courses[j.start].abbrev for j in routes if j.finish == g) for g in courses
            }
            return await inter.response.send_message(
                embed=blue_embed(
                    title="All routes",
                    desc="\n".join(f"**To {k}:**\nfrom {v}" for k, v in by_end_track.items())
                ),
                ephemeral=True
            )
        route_list = [
            g for g in routes if (not from_track or g.start == from_track) and
                                 (not to_track or g.finish == to_track)
        ]
        if not route_list:
            return await inter.response.send_message(
                embed=red_embed(
                    title="This route doesn't exist.",
                    desc=f"There is no route from {from_track} to {to_track}."
                ), ephemeral=True
            )
        return await inter.response.send_message(
            embed=blue_embed(
                title="Routes" + (f" from {from_track}" if from_track else "") +
                      (f" to {to_track}" if to_track else ""),
                desc="\n".join(g.display for g in route_list)
            )
        )

    @discord.app_commands.command(
        name="random",
        description="Get a random route."
    )
    @discord.app_commands.autocomplete(
        from_track=course_autocomplete, to_track=course_autocomplete
    )
    @discord.app_commands.describe(
        from_track="Track name", to_track="Track name"
    )
    @discord.app_commands.rename(
        from_track="from", to_track="to"
    )
    async def random_command(self, inter: discord.Interaction, from_track: str = None, to_track: str = None):
        route_list = [
            g for g in routes if (not from_track or g.start == from_track) and
                                 (not to_track or g.finish == to_track)
        ]
        if not route_list:
            return await inter.response.send_message(
                embed=red_embed(
                    title="This route doesn't exist.",
                    desc=f"There is no route from {from_track} to {to_track}."
                ), ephemeral=True
            )
        ret = choice(route_list)
        return await inter.response.send_message(
            embed=blue_embed(
                title=ret.display,
                desc=("random" + (f" from {from_track}" if from_track else "") +
                      (f" to {to_track}" if to_track else "")) if from_track or to_track else None
            )
        )


async def setup(bot: Bot):
    await bot.add_cog(RouteCog(bot))
