workspace {
  model {
    gamer = person "Gamer"
    gamePlatform = softwareSystem "Gaming Platform" {
      container launcher "Game Launcher"
      container server "Game Server"
      container stats "Statistics DB"
      gamer -> launcher "Starts game"
      launcher -> server "Connects"
      server -> stats "Updates stats"
    }
  }
  views {
    container gamePlatform {
      include *
      autolayout lr
    }
  }
}