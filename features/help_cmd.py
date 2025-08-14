from core.io import Console
from core.state import ChatState


def help_handle(state: ChatState, console: Console, args: list[str]) -> None:

    console.print_sys("Komutlar (kısaca):")
    console.print_sys("  /help                Yardım menüsü")
    console.print_sys("  /log [--last N]      Mesaj geçmişini göster")
    console.print_sys("  /exit (alias: :q)    Çıkış yapar")
    console.print_sys("  --username           Mevcut kullanıcı adını gösterir")
    console.print_sys(
        "  --change_username X  Kullanıcı adını değiştirir (X yoksa sorar)"
    )
