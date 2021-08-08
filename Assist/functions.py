import asyncio
import os
import time

import discord
import numpy as np
import pandas as pd
import pymongo
from pymongo import MongoClient

# functions for constructing
# users must'nt be able to call this
# assigns role
async def default_channel(guild):

    only_admin = { guild.default_role: discord.PermissionOverwrite(read_messages = False) }
    read_only = { guild.default_role: discord.PermissionOverwrite(send_messages = False, add_reactions = False) }
    
    manager_permission = discord.Permissions(manage_channels = True, manage_permissions = True, manage_roles = True,
mute_members = True, add_reactions = True)

    manager = await guild.create_role(name = "Manager" , permissions = manager_permission)

    #send annotations for command text channel
    default_guide = "For Quick Setup of your Server\n"
    default_role = "Added MANAGER role, you may change the name according to your preference\n"
    default_advise = "Do not DELETE Manager role as it is tracked by the bot"

    default_info = default_guide + default_role + default_advise
    await guild.owner.send(default_info)
    
    cl = MongoClient(os.getenv("MONGO_URL"))
    db = cl[os.getenv("CLUSTER")]
    co = db[os.getenv("COLLECTION")]

    query = {"_id": str(guild.id)}
    data = co.find(query)

    # sends data to database of roles
    if not data.count():
        co.insert_one({"_id": str(guild.id), "name": guild.name, "role": {"_id" : str(manager.id), "name": manager.name}})

    return

# functions to use the features of the disc bot for the students
class PUBLIC(object):

    # creates a voice and text channel under the same category w the same name
    async def channel(self, client, message, content):
        guild, channel, member, role = await self.__helper_func(message, content, "channel")

        if guild is None:
            return
        
        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages = False),
member: discord.PermissionOverwrite(manage_channels = True, manage_permissions = True, manage_roles = True,
mute_members = True, read_messages = True)}

        new_category = await guild.create_category(content[1], overwrites=overwrites, position=5)
        new_channel = await guild.create_text_channel(content[1], category=new_category)
        new_voice_channel = await guild.create_voice_channel(content[1], category=new_category)

        await channel.send("Created Channel Successfully at" + guild.name)
        return
    
    # checks attendance
    async def attendance(self, client, message, content):
        guild, channel, member, role = await self.__helper_func(message, content, "attendance")
    
        try:
            if guild is None:
                return

            channels = await guild.fetch_channels()
            target_channel = []

            for _channel in channels:
                if _channel.name == content[1]:
                    if isinstance(_channel, discord.TextChannel):
                        target_channel.append(_channel)
                    
            if len(target_channel) == 0:
                raise NormalError("Target Channel Doesn't Exist")
            
        except NormalError as e:
            await channel.send(e)


        thumb_up = "👍"
        thumb_down = "👎"

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) in [thumb_up, thumb_down]

        for chan in target_channel:
            info = "Attendance Check! Everyone in"
            mes = await chan.send(info + chan.name)

            await mes.add_reaction(thumb_up)

            start = time.time()
            total = 300.00

            while True:
                try:
                    reaction, user = await client.wait_for("reaction_add", timeout = total, check = check)
                    total -= (time.time() - start)

                    if not total:
                        break

                except Exception as e:
                    break

            await chan.send("Done Checking Attendance! Have a good day")

            cache_msg = discord.utils.get(client.cached_messages, id = mes.id)
            reacted = await cache_msg.reactions[0].users().flatten()
            
            default_info = "[{}] Following Students are present\n".format(chan.name)
            default_users = ""
            index = 0
            for u in [u for u in reacted if u.id != mes.author.id]:
                default_users += "[o] {}\n".format( u.name)

            await message.author.send("{}{}".format(default_info,default_users))
            return

    # caculator: add
    async def add(self, client, message, content):
        if len(content) < 3:
            return
        
        guild = message.channel.guild
        channel = message.channel
        author = message.author

        try:
            answer = float(content[1]) + float(content[2])
            await channel.send(answer)

        except Exception as e:
            await channel.send("Invalid Operation")

    # caculator: subtraction
    async def sub(self, client, message, content):
        if len(content) < 3:
            return
        
        guild = message.channel.guild
        channel = message.channel
        author = message.author

        try:
            answer = float(content[1]) - float(content[2])
            await channel.send(answer)

        except Exception as e:
            await channel.send("Invalid Operation")
    
    # caculator: multiplication
    async def mul(self, client, message, content):
        if len(content) < 3:
            return
        
        guild = message.channel.guild
        channel = message.channel
        author = message.author

        try:
            answer = float(content[1]) * float(content[2])
            await channel.send(answer)

        except Exception as e:
            await channel.send("Invalid Operation")
    
    # caculator: division
    async def div(self, client, message, content):
        if len(content) < 3:
            return
        
        guild = message.channel.guild
        channel = message.channel
        author = message.author

        try:
            answer = float(content[1]) / float(content[2])
            await channel.send(answer)

        except Exception as e:
            await channel.send("Invalid Operation")
    
    # caculator: modulo
    async def mod(self, client, message, content):
        if len(content) < 3:
            return
        
        guild = message.channel.guild
        channel = message.channel
        author = message.author

        try:
            answer = float(content[1]) % float(content[2])
            await channel.send(answer)

        except Exception as e:
            await channel.send("Invalid Operation")

    # syntax checker function
    async def __helper_func(self, message, content, caller):
        
        # syntax for functionqq
        # <command_prefix><function_name> <channel> <guild>

        cluster = MongoClient(os.getenv("MONGO_URL"))
        db = cluster[os.getenv("CLUSTER")]
        collection = db[os.getenv("COLLECTION")]

        user = message.author
        channel = message.channel

        try:

            # syntax checking
            # check if user inputted target guild/server
            # return otherwise
            # display error
            if len(content) < 3:
                if caller == "user" and len(content) > 1:
                    raise NormalError("Please Specify Target Server..")
            
            guild_name = content[2]
            guild_ids = {}
            target = collection.find({"name" : guild_name})

            # store all found guild/servers in a dictionary
            for guild in target:
                guild_ids[guild["_id"]] = guild["_id"]

            # target guild/server is not found in the database
            # return otherwise
            # display error
            if len(guild_ids) == 0:
                raise NormalError("Target Server wasn't found...")

            # check if user is a member of target guild/server
            for guild in user.mutual_guilds:
                if str(guild.id) in guild_ids:
                    user_id = user.id  

                    # iterate all members in guild till user is found
                    member = await guild.fetch_member(user_id)

                    if member is None:
                        break
                    
                    manager = collection.find_one({"_id" : str(guild.id)})["role"]["name"]

                    # check if user has role manager
                    for role in member.roles:
                        if manager == role.name:
                            return guild, channel, member, role

                    # user dont have manager role
                    break

            raise NormalError("You do not have permission")

        except NormalError as e:
            await channel.send(e)
        except Exception as e:
            await channel.send("Something went wrong... try again later")

        return None, None, None, None

# custom exceptions
class NormalError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
