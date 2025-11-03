workspace {
  model {
    customer = person "Customer"
    ecommerce = softwareSystem "E-Commerce" {
      frontend = container "Frontend"
      backend = container "Backend"
      customer -> frontend "Browses"
      frontend -> backend "Requests"
    }
  }
  views {
    container ecommerce {
      include *
      autolayout lr
    }
  }
}