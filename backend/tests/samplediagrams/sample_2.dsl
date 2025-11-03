workspace {
  model {
    admin = person "Admin"
    system = softwareSystem "System B" {
      container api "API Server"
      container cache "Cache"
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