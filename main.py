import asyncio, sys
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from nuker import run_nuke, load_config, save_config

console = Console()
DRY = "--dry-run" in sys.argv

def show_config(cfg):
    t = Table(title="Current Config"); t.add_column("Key"); t.add_column("Value")
    for k, v in cfg.items(): t.add_row(k, str(v))
    console.print(t)

def edit_config(cfg):
    while True:
        show_config(cfg)
        choice = Prompt.ask("Edit which?",
            choices=["channel_name", "message", "advertise", "spam_count", "done"], default="done")
        if choice == "done":
            save_config(cfg); console.print("[green]Saved.[/]"); return cfg
        if choice == "advertise":
            cfg["advertise"] = Confirm.ask("Enable advertising?", default=cfg["advertise"])
        elif choice == "spam_count":
            cfg["spam_count"] = IntPrompt.ask("Messages per channel", default=cfg["spam_count"])
        else:
            cfg[choice] = Prompt.ask(choice, default=cfg[choice])

def main():
		console.rule("[bold magenta]GRIM NUKER[/]")
    if DRY: console.print("[bold yellow]DRY RUN — nothing will actually be deleted[/]")
    cfg = load_config()

    while True:
        token = Prompt.ask("[bold]Bot token[/] [dim](enter to quit)[/]", default="")
        if not token: break
        if Confirm.ask("Edit config before nuking?", default=False):
            cfg = edit_config(cfg)
        console.print("[bold]Config:[/]", cfg, "\n")
        if not Confirm.ask("[red]NUKE NOW?[/]", default=True): continue
        asyncio.run(run_nuke(token, cfg, console, DRY))
        console.print("\n[bold green]Finished.[/] Paste another token or hit enter to quit.\n")

if __name__ == "__main__":
    main()