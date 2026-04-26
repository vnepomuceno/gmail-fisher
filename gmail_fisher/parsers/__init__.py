from gmail_fisher import console


def print_header(title: str):
    console.print()
    console.rule(f"[bold cyan]{title}[/bold cyan]", style="cyan")
    console.print()
