.. _unit_test:

Unit Tests
==========

Unit tests in ``pipobot`` module are based on the python ``unittest`` library.
On top of that library, a ``ModuleTest`` class has been written to provide some bot-related
functionalities.

For more information about the ModuleTest class see :ref:`module_test`.

Write a ModuleTest class
------------------------

Some tools are provided to you to write a unit test.
First you can use the `bot_answer` method that will take a string defining what is
the message that must be analysed by the bot, and retuning its answer.
Then you can use `unittest` functionalities to check if the result is correct.
Each test is a method that must be prefixed with *test_*
Here is a first simple example: ::

   class BandMTest(ModuleTest):
       def test_current(self):
           """ !b&m : check current song """
           bot_rep = self.bot_answer("!b&m")
           self.assertRegexpMatches(bot_rep, "Titre en cours : (.*)")

       def test_lyrics(self):
           """ !b&m lyrics """
           self.bot_answer("!b&m lyrics")


This ModuleTest contains 2 unit test : the first is asking the bot *!b&m* and expects in return
a result matching a regular expression.
The second test is asking *!b&m lyrics* and has no test on the output : it will only fail an exception
is raised.

You can also create more complicated example : for instance to test modules that need to access
to database elements : ::

    class TodoRemove(ModuleTest):
        def setUp(self):
            """ Creates 3 random todo we add manually to the database """
            self.todos = []
            todos = {string_gen(8): string_gen(50),
                     string_gen(8): string_gen(50),
                     string_gen(8): string_gen(50)}
            for list_name, todo in todos.iteritems():
                todo = Todo(list_name, todo, "sender", time.time())
                self.bot.session.add(todo)
                self.bot.session.commit()
                self.todos.append(todo)

        def test_todo_remove(self):
            """ !todo remove """
            bot_rep = self.bot_answer("!todo remove %s" % ",".join([str(elt.id) for elt in self.todos]))
            expected = "\n".join(["%s a été supprimé" % todo for todo in self.todos])
            self.assertEqual(bot_rep, expected)

        def tearDown(self):
            """ In case of failure, we manually remove the todo we added """
            for todo in self.todos:
                remove = self.bot.session.query(Todo).filter(Todo.id == todo.id).first()
                if remove is not None:
                    self.bot.session.delete(remove)
                    self.bot.session.commit()

In this class, we are only testing one command with the method `test_todo_remove`.
The setUp and tearDown methods are defined in the python `unittest` API : 

    * setUp is executed *before* the actual test
    * tearDown is executed *after* the test

In the test we want to try the deletion of todo, with the "!todo remove id1,id2,id3" command.
So in the setUp we manually create 3 todos with random values. Then in the test we try to remove them.
The tearDown is usefull in case of the test fails : it manually removes todo added in the setUp, so 
we are sure that even if the test fails we will not have any generated todo remaining in the database.

Run your tests
--------------

To ask the bot to run the test you have just created, use the `--unit-test` option of pipobot, 
as described here: :ref:`unit_test_mode`.
