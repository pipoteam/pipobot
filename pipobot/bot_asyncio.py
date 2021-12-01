#-*- coding: utf-8 -*-
"""This module contains a class to test the bot in a CLI mode"""

import asyncio
import logging
import random

from pipobot.bot_test import TestBot
from pipobot.lib.utils import color


nickname_colors = ["blue", "cyan", "red", "purple", "yellow"]
nickname_colors.extend(["bright %s" % col for col in nickname_colors])
log = logging.getLogger(__name__)


class TestOutput:
    """
    In Pipobot, this is used as a queue.Queue.
    Here, when something is added to it, we will just send the message to
    every client connected (method `put`).
    """
    def __init__(self, bot):
        self.bot = bot

    def put(self, msg):
        """
        Called whenever a message is added to the queue.
        Broadcast it to all clients
        """
        # XXX why is this test necessary ???
        if msg is not None and msg != "":
            msg = "%s %s\n" % (color("<%s>" % self.bot.name, self.bot.color),
                               msg)
            for cl in self.bot.clients.values():
                cl.write(msg)


class Client:
    """
    A client connected to the bot :
        - reader/writer are attibutes used on the 'stream' level
        - name/jid/role will be sent by the client later (see `decode_name`)
    """
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.name = None
        self.jid = None
        self.role = None
        self.color = random.choice(nickname_colors)

    def decode_name(self, msg):
        """
        Decode the "authentication" message sent by the client
        It is supposed to be : 'username;jid;role'
        """
        try:
            username, jid, role = msg.strip().split(";")
            self.name = username
            self.jid = jid
            self.role = role
            return True
        except ValueError:
            return

    def write(self, msg):
        """ Send the message on the asyncio stream writer """
        self.writer.write(msg.encode())


class AsyncioBot(TestBot):
    def __init__(self, name, login, chatname, modules, session):
        output = TestOutput(self)
        TestBot.__init__(self, name, login, chatname, modules, session, output)
        self.clients = {}
        self.color = random.choice(nickname_colors)

    def accept_client(self, client_reader, client_writer):
        """ Called whenever a new client is connected to the bot """
        client = Client(client_reader, client_writer)
        task = asyncio.Task(self.handle_client(client))
        self.clients[task] = client

        def client_done(task):
            """ Called when a client is disconnecting """
            del self.clients[task]
            client_writer.close()
            log.info("End Connection")

        log.info("New Connection")
        task.add_done_callback(client_done)

    def extract_data(self, data):
        """ Take the result of asyncio.wait and extract the result of the Task """
        # wait for input from client
        if data is None:
            log.warning("Received no data")
            return
        task = data[0].pop()
        data = task.result()

        sdata = data.decode().rstrip()
        log.warning("Received %s" % sdata)
        return sdata

    @asyncio.coroutine
    def handle_client(self, client):
        """
        Coroutine used to manage every client :
            - Welcome him
            - Ask him its name;jid;role
            - Wait for its messages, broadcast it to every other client, send it message to the bot,
              broadcast the bot answer
        """

        # wait for the client to send nickname;jid;role
        data = yield from asyncio.wait([client.reader.readline()])

        if data is None:
            log.warning("Expected username;jid;role, received None")
            client.write("You were supposed to send me username;jid;role. You failed. Adios !\n")
            return

        sdata = self.extract_data(data)
        ret = client.decode_name(sdata)
        if ret is None:
            log.warning("Expected username;jid;role, received '%s'", sdata)
            return

        self.occupants.add_user(client.name, client.jid, client.role)

        for cl in self.clients.values():
            if cl != client:
                cl.write("*** %s has joined\n" % client.name)
            else:
                cl.write("Welcome %s\n" % client.name)

        while True:
            # wait for input from client
            data = yield from asyncio.wait([client.reader.readline()])
            sdata = self.extract_data(data)

            if sdata in ("QUIT", ""):
                break
            # broadcast the message to every other clients
            for cl in self.clients.values():
                msg = "%s %s\n" % (color("<%s>" % client.name, client.color),
                                   sdata)
                if cl != client:
                    cl.write(msg)

            # This will create a thread to manage the message
            # The result is written in self.output, the method MyOutput.put
            # will handle the dispatch of the message
            self.create_msg(client.name, sdata)

    def say(self, *args, **kwargs):
        self.output.put(args[0])
