import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { Header } from '@/components/layout/Header'
import { Footer } from '@/components/layout/Footer'
import { Home } from '@/pages/Home'
import { BookDetails } from '@/pages/BookDetails'
import { Search } from '@/pages/Search'
import { Cart } from '@/pages/Cart'
import { Checkout } from '@/pages/Checkout'
import { OrderConfirmation } from '@/pages/OrderConfirmation'
import { Profile } from '@/pages/Profile'
import { Login } from '@/pages/Login'
import { Register } from '@/pages/Register'
import MyOrders from '@/pages/MyOrders'
import Shipping from '@/pages/Shipping.tsx'
import { AdminDashboard } from '@/pages/Admin/Dashboard'
import { BookManagement } from '@/pages/Admin/BookManagement'

function App() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/books/:id" element={<BookDetails />} />
          <Route path="/search" element={<Search />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/checkout/success/:orderId" element={<OrderConfirmation />} />
          <Route path="/orders" element={<MyOrders />} />
          <Route path="/shipping" element={<Shipping />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/books" element={<BookManagement />} />
        </Routes>
      </main>
      <Footer />
      <Toaster />
    </div>
  )
}

export default App
