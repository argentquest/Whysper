workspace {
  model {
    user = person "User"
    chat = softwareSystem "Chat App" {
      client = container "Client"
      server = container "Server"
      user -> client "Sends message"
      client -> server "Delivers message"
    }
  }
  views {
    container chat {
      include *
      autolayout lr
    }
  }
}