import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { Header } from '@/components/layout/Header'
import { Footer } from '@/components/layout/Footer'
import { ProtectedRoute } from '@/components/common/ProtectedRoute'
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
import Shipping from '@/pages/Shipping'
import { AdminDashboard } from '@/pages/Admin/Dashboard'
import { BookManagement } from '@/pages/Admin/BookManagement'
import Config from '@/pages/Config'

function App() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/books/:id" element={<BookDetails />} />
          <Route path="/search" element={<Search />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected Routes */}
          <Route path="/cart" element={<ProtectedRoute><Cart /></ProtectedRoute>} />
          <Route path="/checkout" element={<ProtectedRoute><Checkout /></ProtectedRoute>} />
          <Route path="/checkout/success/:orderId" element={<ProtectedRoute><OrderConfirmation /></ProtectedRoute>} />
          <Route path="/orders" element={<ProtectedRoute><MyOrders /></ProtectedRoute>} />
          <Route path="/shipping" element={<ProtectedRoute><Shipping /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/config" element={<ProtectedRoute><Config /></ProtectedRoute>} />
          
          {/* Admin Routes */}
          <Route path="/admin" element={<ProtectedRoute requireAdmin><AdminDashboard /></ProtectedRoute>} />
          <Route path="/admin/books" element={<ProtectedRoute requireAdmin><BookManagement /></ProtectedRoute>} />
        </Routes>
      </main>
      <Footer />
      <Toaster />
    </div>
  )
}

export default App
