workspace {
  model {
    customer = person "Customer"
    ecommerce = softwareSystem "E-Commerce Platform" {
      container frontend "Frontend"
      container backend "Backend"
      container payment "Payment Gateway"
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