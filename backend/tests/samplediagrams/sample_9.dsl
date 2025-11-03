workspace {
  model {
    gamer = person "Gamer"
    gamePlatform = softwareSystem "Gaming Platform" {
      launcher = container "Game Launcher"
      server = container "Game Server"
      stats = container "Statistics DB"
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