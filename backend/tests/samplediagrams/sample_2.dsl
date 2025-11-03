workspace {
  model {
    admin = person "Admin"
    system = softwareSystem "System B" {
      api = container "API Server"
      cache = container "Cache"
      admin -> api "Manages"
      api -> cache "Stores data"
    }
  }
  views {
    container system {
      include *
      autolayout lr
    }
  }
}