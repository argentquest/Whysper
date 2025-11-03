workspace {
      model {
        gamer = person "Gamer"
        gamePlatform = softwareSystem "Gaming Platform" {
          launcher = container "Game Launcher"
          server = container "Game Server"
          statsDB = container "Statistics DB"
          gamer -> launcher "Launches games"
          launcher -> server "Connects"
          server -> statsDB "Stores stats"
        }
      }
      views {
        container gamePlatform {
          include *
          autolayout lr
        }
      }
    }