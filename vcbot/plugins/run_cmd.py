from pyrogram import filters
import traceback
import sys
import os
import re
import subprocess
from io import StringIO, BytesIO
from vcbot import UB, Var

p = print

async def aexec(code, c, m):
    exec(
        f'async def __aexec(c, m):' + '\n rm = m.reply_to_message' +
        ''.join(f'\n {l}' for l in code.split('\n'))
    )
    return await locals()['__aexec'](c, m)


@UB.on_message(filters.user(Var.SUDO) & filters.command("eval", '!'))
async def evaluate(client, message):
    status_message = await message.reply_text("`Running ...`")
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await status_message.delete()
        return
    reply_to_id = message.message_id
    if message.reply_to_message:
        reply_to_id = message.reply_to_message.message_id
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = f"<b>OUTPUT</b>:\n<code>{evaluation.strip()}</code>"
    if len(final_output) > 4096:
        _file = BytesIO()
        _file.name = 'output.txt'
        _file.write(str(final_output))
        await message.reply_document(
            document=_file,
            caption=f"<code>{cmd}</code>",
            disable_notification=True,
            reply_to_message_id=reply_to_id
        )
        await status_message.delete()
    else:
        await status_message.edit(final_output)



@UB.on_message(filters.user(Var.SUDO) & filters.command("term", '!'))
async def terminal(client, message):
    if len(message.text.split()) == 1:
        await message.reply("Usage: `/term echo owo`")
        return
    args = message.text.split(None, 1)
    teks = args[1]
    if "\n" in teks:
        code = teks.split("\n")
        output = ""
        for x in code:
            shell = re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', x)
            try:
                process = subprocess.Popen(
                    shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except Exception as err:
                print(err)
                await message.reply("""
**Error:**
```{}```
""".format(err))
            output += "**{}**\n".format(code)
            output += process.stdout.read()[:-1].decode("utf-8")
            output += "\n"
    else:
        shell = re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', teks)
        for a in range(len(shell)):
            shell[a] = shell[a].replace('"', "")
        try:
            process = subprocess.Popen(
                shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(etype=exc_type, value=exc_obj, tb=exc_tb)
            await message.reply("""<b>Error:</b>\n<code>{}</code>""".format("".join(errors)))
            return
        output = process.stdout.read()[:-1].decode("utf-8")
    if str(output) == "\n":
        output = None
    if output:
        if len(output) > 4096:
            _file = BytesIO()
            _file.name = 'output.txt'
            _file.write(str(output))
            await client.send_document(message.chat.id, _file, reply_to_message_id=message.message_id, caption=f"<code>{message.text}</code>")
            return
        await message.reply(f"<b>Output:</b>\n<code>{output}</code>", parse_mode='HTML')
    else:
        await message.reply("<b>Output:</b>\n<code>No Output</code>")