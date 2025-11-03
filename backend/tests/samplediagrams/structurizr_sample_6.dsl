workspace {
  model {
    user = person "User"
    blog = softwareSystem "Blog Platform" {
      frontend = container "Frontend"
      backend = container "Backend"
      db = container "Database"
      user -> frontend "Reads articles"
      frontend -> backend "Requests"
      backend -> db "Stores data"
    }
  }
  views {
    container blog {
      include *
      autolayout lr
    }
  }
}