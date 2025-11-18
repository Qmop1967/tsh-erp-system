export function SimpleUsersTest() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-blue-600">
        ✅ HR Users Page is Working!
      </h1>
      <p className="mt-4 text-gray-600">
        This confirms that the routing to /hr/users is working correctly.
      </p>
      <div className="mt-6 bg-green-100 p-4 rounded-lg">
        <h2 className="font-semibold text-green-800">Route Test Successful</h2>
        <p className="text-green-700">The HR Users route is accessible via /hr/users</p>
      </div>
    </div>
  )
}
