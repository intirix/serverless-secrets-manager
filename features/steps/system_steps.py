from behave import given
import system


@given(u'user "{username}" exists')
def step_impl(context, username):
    mysys: system.System = context.system
    mysys.addUser(username, username)


@given(u'user "{username}" has a keypair with password "{password}"')
def step_impl(context, username, password):
    mysys: system.System = context.system
    mysys.generateKeysForUser(username, password)


@given(u'user "{username}" can login with a password')
def step_impl(context, username):
    mysys: system.System = context.system
    mysys.enablePasswordAuth(username)
