import React, { useState, useEffect } from "react";
import axios from "axios";
import config from "../config";

// StarRating component showing the rating for the user
function StarRating({ rating }) {
  const stars = [];
  for (let i = 1; i <= rating; i++) {
    stars.push(
      <span key={i} className={i <= rating ? "text-warning" : "text-muted"}>
        &#9733; {/* Star character */}
      </span>
    );
  }
  return <div>{stars}</div>;
}

function Profile({ user }) {
  const [activeListings, setActiveListings] = useState([]);
  const [shoppingCart, setShoppingCart] = useState([]);
  const [bidHistory, setBidHistory] = useState([]);
  const [userInfo, setUserInfo] = useState([]);
  const [activeUsers, setActiveUsers] = useState([]);
  const [watchlist, setWatchlist] = useState([]);

  const [lowerPrice, setLowerPrice] = useState("");
  const [upperPrice, setUpperPrice] = useState("");
  const [keyword, setKeyword] = useState("");

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [dateList, setDateList] = useState([]);

  const [newCategory, setNewCategory] = useState("");

  const [toLinkListingID, setToLinkListingID] = useState("");
  const [toLinkCategory, setToLinkCategory] = useState("");

  const handleSuspendUser = async (userID) => {
    try {
      const response = await axios.post("http://localhost:9990/suspend-user", {
        user_id: userID,
      });
      if (response.data.success) {
        // Update your UI here to reflect the suspension
        setActiveUsers((currentUsers) =>
          currentUsers.map((user) => {
            if (user.userID === userID) {
              return { ...user, isActive: false }; // or simply remove the user from the list
            }
            return user;
          })
        );
        alert(`User ${userID} suspended successfully`);
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      alert("Error suspending user: " + error.message);
    }
  };

  const handleCheckout = async (listingID) => {
    try {
      const response = await axios.post("http://localhost:9991/checkout", {
        listingID,
      });
      if (response.data.success) {
        // Update your UI here, e.g., remove the listing from shoppingCart
        setShoppingCart((currentListings) =>
          currentListings.filter((listing) => listing.listingID !== listingID)
        );
        alert("Checkout successful");
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      alert("Error during checkout: " + error.message);
    }
  };

  const handleRemoveListing = async (listingID) => {
    try {
      const response = await axios.post(
        "http://localhost:9991/terminate-listing",
        { listingID }
      );
      if (response.data.success) {
        setActiveListings((currentListings) =>
          currentListings.filter((listing) => listing.listingID !== listingID)
        );
        alert("Listing removed successfully");
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      alert(
        "Error removing listing: You cannot remove an item already has been bid."
      );
    }
  };

  const handleEndListing = async (listingID) => {
    try {
      const response = await axios.post("http://localhost:9991/end-listing", {
        listingID,
      });
      if (response.data.success) {
        setActiveListings((currentListings) =>
          currentListings.filter((listing) => listing.listingID !== listingID)
        );
        alert("Listing ended successfully");
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      alert("Error ending listing: You cannot end an auction without bid.");
    }
  };

  const handleCategorizeSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post(
        "http://localhost:9991/categorize-listing",
        {
          listingID: toLinkListingID,
          category: toLinkCategory,
        }
      );
      alert("Listing categorized successfully!");
      // Optionally reset the state here if needed
    } catch (error) {
      alert("Error in categorizing listing: " + error.message);
    }
  };

  const handleWatchlistSubmit = () => {
    const data = {
      userID: user.id,
      keyword: keyword,
      lowerPrice: lowerPrice,
      upperPrice: upperPrice,
    };

    axios
      .post("http://localhost:9991/add-watchlist", data)
      .then((response) => {
        alert("Watchlist created successfully!");
      })
      .catch((error) => {
        alert("Error creating watchlist: " + error.message);
      });
  };

  const handleFilterSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post(
        "http://localhost:9991/search-by-time",
        {
          filterStartDate: startDate,
          filterEndDate: endDate,
        }
      );
      setDateList(response.data.data);
    } catch (error) {
      alert("Error fetching the list: " + error.message);
    }
  };

  const handleNewCategorySubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post("http://localhost:9991/add-category", {
        new_category: newCategory,
      });
      alert("Category added successfully!");
      setNewCategory("");
    } catch (error) {
      alert("Error adding category: " + error.message);
    }
  };

  useEffect(() => {
    if (!user || !user.id) return;
    axios
      .get(`${config.userServiceUrl}/user/${user.id}/profile`)
      .then((response) => {
        if (response.data.success) {
          setUserInfo(response.data.data);
        }
      })
      .catch((error) => console.log(error));

    axios
      .get(`${config.userServiceUrl}/user/${user.id}/active-listings`)
      .then((response) => {
        setActiveListings(response.data.data);
      })
      .catch((error) => console.log(error));

    axios
      .get(`${config.userServiceUrl}/user/${user.id}/bid-history`)
      .then((response) => {
        setBidHistory(response.data.data);
      })
      .catch((error) => console.log(error));

    axios
      .get(`${config.userServiceUrl}/user/${user.id}/active-users`)
      .then((response) => {
        if (response.data.success) {
          setActiveUsers(response.data.data);
        }
      })
      .catch((error) => console.log(error));

    axios
      .post(`${config.itemServiceUrl}/get-shoppingcart`, { userID: user.id })
      .then((response) => {
        setShoppingCart(response.data.data);
      })
      .catch((error) => console.log(error));

    axios
      .post(`${config.itemServiceUrl}/get-watchlist`, { userID: user.id })
      .then((response) => {
        setWatchlist(response.data.data);
      })
      .catch((error) => console.log(error));
  }, [user, user.id]);

  if (!userInfo) {
    return <div>Loading...</div>;
  } else {
    console.log(userInfo);
  }

  return (
    <div className="container pt-5">
      <h1>{userInfo.firstName}'s Profile</h1>

      {/* Basic info of the user */}
      <div className="mt-4">
        <h4 style={{ color: "maroon" }}>Profile Details</h4>
        <div className="row">
          <div className="col-4">
            <label>First Name</label>
            <input
              type="text"
              className="form-control"
              value={userInfo.firstName}
              disabled
            />
          </div>
          <div className="col-4">
            <label>Last Name</label>
            <input
              type="text"
              className="form-control"
              value={userInfo.lastName}
              disabled
            />
          </div>
        </div>
        <div className="row mt-2">
          <div className="col-4">
            <label>Email</label>
            <input
              type="email"
              className="form-control"
              value={userInfo.email}
              disabled
            />
          </div>
        </div>
        <div className="row mt-2">
          <div className="col-4">
            <label>Username</label>
            <input
              type="text"
              className="form-control"
              value={userInfo.userName}
              disabled
            />
          </div>
        </div>
        <div className="row mt-2">
          <div className="col-4">
            <label>Date Joined</label>
            <input
              type="text"
              className="form-control"
              value={new Date(userInfo.dateJoined).toLocaleDateString()}
              disabled
            />
          </div>
        </div>
        <div className="row mt-2">
          <div className="col-4">
            <label>User Rating</label>
            <div className="form-control" style={{ padding: "7px" }}>
              <StarRating rating={parseFloat(userInfo.rating)} />
              <small>{userInfo.rating}/5.0</small>
            </div>
          </div>
        </div>
        <div className="row mt-2">
          <div className="col-4">
            <label>Account Status</label>
            <input
              type="text"
              className="form-control"
              value={userInfo.isActive ? "Active" : "Inactive"}
              disabled
            />
          </div>
        </div>
        <div className="row mt-2">
          <div className="col-4">
            <label>Admin Status</label>
            <input
              type="text"
              className="form-control"
              value={userInfo.isAdmin ? "Admin" : "User"}
              disabled
            />
          </div>
        </div>
      </div>

      <div className="mt-5">
        <h4 style={{ color: "maroon" }}>Active Listings</h4>
        <table className="table table-striped table-hover">
          <thead>
            <tr>
              <th>#</th>
              <th>Listing ID</th>
              <th>Item</th>
              <th>Current Bid</th>
              <th>Start Price</th>
              <th>Expires</th>
              <th>Number Flagged</th>
              <th>Remove Auction</th>
              <th>End Auction</th>
            </tr>
          </thead>
          <tbody>
            {activeListings.map((listing, index) => (
              <tr key={listing.listingID}>
                <th>{index + 1}</th>
                <td>{listing.listingID}</td>
                <td>{listing.name}</td>
                <td>{listing.bidAmt}</td>
                <td>{listing.startPrice}</td>
                <td>{new Date(listing.endDate).toLocaleDateString()}</td>
                <td>{listing.numFlagged}</td>
                <td>
                  <button
                    className="btn btn-danger"
                    onClick={() => handleRemoveListing(listing.listingID)}
                  >
                    Remove
                  </button>
                </td>
                <td>
                  {user.isAdmin ? (
                    <button
                      className="btn btn-danger"
                      onClick={() => handleEndListing(listing.listingID)}
                    >
                      End
                    </button>
                  ) : (
                    <button
                      className="btn btn-danger"
                      // onClick={() => handleEndListing(listing.listingID)}
                    >
                      End
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div>
        <h4 style={{ color: "maroon" }}>
          Categorize a Listing (Use existing category and listingID
        </h4>
        <form onSubmit={handleCategorizeSubmit}>
          <input
            type="text"
            placeholder="Listing ID"
            value={toLinkListingID}
            onChange={(e) => setToLinkListingID(e.target.value)}
          />
          <input
            type="text"
            placeholder="Category"
            value={toLinkCategory}
            onChange={(e) => setToLinkCategory(e.target.value)}
          />
          <button type="submit">Categorize</button>
        </form>
      </div>

      {user.isAdmin && (
        <div className="mt-5">
          <h4 style={{ color: "maroon" }}>Closed Listings</h4>
          <form onSubmit={handleFilterSubmit}>
            <label>
              End date from:
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </label>
            <label>
              to:
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </label>
            <button type="submit">Search</button>
          </form>

          <table className="table table-striped table-hover">
            <thead>
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>Bid Amount</th>
                <th>Start Price</th>
                <th>End Date</th>
                <th>ShippingCosts</th>
                <th>NUmber of Flags</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {dateList.map((listing, index) => (
                <tr key={listing.listingID}>
                  <th>{index + 1}</th>
                  <td>{listing.name}</td>
                  <td>{listing.bidAmt}</td>
                  <td>{listing.startPrice}</td>
                  <td>{listing.endDate}</td>
                  <td>{listing.shippingCosts}</td>
                  <td>{listing.numFlagged}</td>
                  <td>{listing.status}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <h4 style={{ color: "maroon" }}>Create New Category</h4>
          <form onSubmit={handleNewCategorySubmit}>
            <input
              type="text"
              placeholder="Enter category name"
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
            />
            <button type="submit">Create</button>
          </form>
        </div>
      )}

      {/* Bid history Table - Only render for normal users */}
      {!user.isAdmin && (
        <div className="mt-5">
          <h4 style={{ color: "maroon" }}>Bid History</h4>
          <table className="table table-striped table-hover">
            <thead>
              <tr>
                <th>Date Placed</th>
                <th>Item</th>
                <th>Bid Amount</th>
              </tr>
            </thead>
            <tbody>
              {bidHistory.map((bid) => (
                <tr key={bid.bidID}>
                  <td>{new Date(bid.bidDate).toLocaleDateString()}</td>
                  <td>{bid.name}</td>
                  <td>{bid.bidAmt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* User Management Table - for all users */}
      <div className="mt-5">
        <h4 style={{ color: "maroon" }}>User Management</h4>
        <table className="table table-striped table-hover">
          <thead>
            <tr>
              <th>#</th>
              <th>User</th>
              <th>First Name</th>
              <th>Last Name</th>
              <th>Date Joined</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {activeUsers.map((user, index) => (
              <tr key={user.userID}>
                <th scope="row">{index + 1}</th>
                <td>{user.userName}</td>
                <td>{user.firstName}</td>
                <td>{user.lastName}</td>
                <td>{new Date(user.dateJoined).toLocaleDateString()}</td>
                <td>
                  {/* Attach the handleSuspendUser function to the onClick event of the button */}
                  <button
                    className="btn btn-danger"
                    onClick={() => handleSuspendUser(user.userID)}
                  >
                    Suspend
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Shopping Cart Table - Only render for normal users */}
      {!user.isAdmin && (
        <div className="mt-5">
          <h4 style={{ color: "maroon" }}>Shopping Cart</h4>
          <table className="table table-striped table-hover">
            <thead>
              <tr>
                <th>#</th>
                <th>Item</th>
                <th>End Data</th>
                <th>Deal Price</th>
                <th>Shipping Costs</th>
                <th>Quantity</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {shoppingCart.map((listing, index) => (
                <tr key={listing.listingID}>
                  <th>{index + 1}</th>
                  <td>{listing.name}</td>
                  <td>{listing.endDate}</td>
                  <td>{listing.dealPrice}</td>
                  <td>{listing.shippingCosts}</td>
                  <td>{listing.quantity}</td>
                  <td>{listing.description}</td>
                  <td>
                    <button
                      className="btn btn-danger"
                      onClick={() => handleCheckout(listing.listingID)}
                    >
                      Check Out
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <h4 style={{ color: "maroon" }}>Watchlist</h4>
          <table className="table table-striped table-hover">
            <thead>
              <tr>
                <th>#</th>
                <th>Lower Price</th>
                <th>Upper Price</th>
                <th>Keywords</th>
              </tr>
            </thead>
            <tbody>
              {watchlist.map((listing, index) => (
                <tr key={listing.watchlistID}>
                  <th>{index + 1}</th>
                  <td>{listing.lowerPrice}</td>
                  <td>{listing.upperPrice}</td>
                  <td>{listing.keyword}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div>
            <input
              type="text"
              placeholder="Lower Price"
              value={lowerPrice}
              onChange={(e) => setLowerPrice(e.target.value)}
            />
            <input
              type="text"
              placeholder="Upper Price"
              value={upperPrice}
              onChange={(e) => setUpperPrice(e.target.value)}
            />
            <input
              type="text"
              placeholder="Keyword"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
            />
            <button onClick={handleWatchlistSubmit}>Create Watchlist</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Profile;
