workspace {
  model {
    customer = person "Customer"
    ecommerce = softwareSystem "E-Commerce Platform" {
      frontend = container "Frontend"
      backend = container "Backend"
      payment = container "Payment Gateway"
      customer -> frontend "Browses"
      frontend -> backend "Requests"
      backend -> payment "Processes payment"
    }
  }
  views {
    container ecommerce {
      include *
      autolayout lr
    }
  }
}