workspace {
      model {
        user = person "User"
        chatApp = softwareSystem "Chat Application" {
          client = container "Client App"
          server = container "Chat Server"
          store = container "Message Store"
          user -> client "Sends messages"
          client -> server "Delivers"
          server -> store "Stores messages"
        }
      }
      views {
        container chatApp {
          include *
          autolayout lr
        }
      }
    }