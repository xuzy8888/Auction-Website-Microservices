import React, { useState, useEffect } from "react";
import axios from "axios";
import config from "../config";
import useLocalStorage from "../hooks/useLocalStorage";

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function Listings() {
  const [listings, setListings] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredResults, setFilteredResults] = useState([]);
  const [hasResults, setHasResults] = useState(true);
  const [bidAmounts, setBidAmounts] = useState({});
  const [user, _] = useLocalStorage("user", {});
  const [activeListings, setActiveListings] = useState([]);

  const handleBidSubmit = (listingID) => {
    const bidAmount = bidAmounts[listingID];
    const url = `${config.auctionServiceUrl}/place-bid/${listingID}`;

    axios
      .post(
        url,
        {
          bidAmt: bidAmount,
          userID: user.id
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      )
      .then((response) => {
        console.log("Bid placed successfully", response);
        setBidAmounts((prevBidAmounts) => ({
          ...prevBidAmounts,
          [listingID]: "",
        }));
      })
      .catch((error) => {
        console.error("Error placing bid", error);
      });
  };

  const handleBidAmountChange = (listingID, amount) => {
    setBidAmounts((prevBidAmounts) => ({
      ...prevBidAmounts,
      [listingID]: amount,
    }));
  };

  const handleBuyNow = async (listingID) => {
    console.log("Buy Now clicked for item:");

    const listing = listings.find(item => item.listingID === listingID);
    const bidAmount = listing.buyNowPrice;
    const url = `${config.auctionServiceUrl}/place-bid/${listingID}`;

    axios
      .post(
        url,
        {
          bidAmt: bidAmount,
          userID: user.id
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      )
      .then((response) => {
        console.log("Bid placed successfully", response);
        setBidAmounts((prevBidAmounts) => ({
          ...prevBidAmounts,
          [listingID]: "",
        }));
      })
      .catch((error) => {
        console.error("Error placing bid", error);
      });
    
    await delay(500);

    try {
      const response = await axios.post("http://localhost:9991/end-listing", {
        listingID,
      });
      if (response.data.success) {
        setActiveListings((currentListings) =>
          currentListings.filter((listing) => listing.listingID !== listingID)
        );
        alert("Buy it now successfully");
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      alert("Error ending listing: You cannot end an auction without bid.");
    }
  };

  const handleFlag = (listingID) => {
    console.log("Flag clicked for item");
    const url = `${config.itemServiceUrl}/flag-listing`;

    axios
      .post(
        url,
        {
          listingID: listingID,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      )
      .then((response) => {
        console.log("flag successfully", response);
      })
      .catch((error) => {
        console.error("Error flag", error);
      });
  };
  useEffect(() => {
    // Fetch all listings
    axios
      .get(`${config.itemServiceUrl}/listings`)
      .then((response) => {
        setListings(response.data.data);
        setFilteredResults(response.data.data); // Default to showing all listings
        setHasResults(response.data.data.length > 0);
      })
      .catch((error) => {
        console.error("There was an error fetching the listings!", error);
      });
  }, []);

  console.log("Filtered Results:", filteredResults);

  const formatDate = (dateString) => {
    const options = { year: "numeric", month: "long", day: "numeric" };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (!searchQuery) {
      setFilteredResults(listings);
      setHasResults(listings.length > 0);
    } else {
      axios
        .post(`${config.itemServiceUrl}/search`, { searchquery: searchQuery })
        .then((response) => {
          setFilteredResults(response.data.data);
          setHasResults(response.data.data.length > 0);
        })
        .catch((error) => {
          console.error("There was an error in the search!", error);
          setFilteredResults([]);
          setHasResults(false);
        });
    }
  };

  return (
    <>
      <div className="container px-5 py-3 my-4">
        <h1 className="text-center">Active Listings</h1>
        <form onSubmit={handleSearch}>
          <div className="row justify-content-center my-3">
            <div className="col-6">
              <div className="input-group">
                <input
                  type="search"
                  className="form-control"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search listings by name or category"
                />
                <button className="main-button" type="submit">
                  Search
                </button>
              </div>
            </div>
          </div>
        </form>
        {hasResults ? (
          <div className="row row-cols-1 row-cols-md-2 g-4 px-3">
            {filteredResults.map((item) => (
              <div className="col" key={item.listingID}>
                <div className="card h-100">
                  <img
                    src={config.itemServiceUrl + "/" + item.photoPath}
                    className="card-img-top"
                    alt={item.name}
                  />
                  {/*<img src={item.photoPath ? process.env.PUBLIC_URL + item.photoPath :*/}
                  {/*    process.env.PUBLIC_URL + '/static/img/No_image_available.jpg'}*/}
                  {/*     className="card-img-top" alt={item.name} />*/}
                  <div className="card-body">
                    <h4 className="card-title">{item.name}</h4>
                    <p className="card-subtitle mb-2 text-muted">
                      {item.description || "No description"}
                    </p>
                    <p className="card-subtitle mb-2 text-muted">
                      Start Price: ${item.startPrice || "N/A"}
                    </p>
                    <p className="card-subtitle mb-2 text-muted">
                      Quantity: {item.quantity}
                    </p>
                    <p className="card-subtitle mb-2 text-muted">
                      Shipping Costs: ${item.shippingCosts}
                    </p>
                    <p className="card-subtitle mb-2 text-muted">
                      Ends: {formatDate(item.endDate)}
                    </p>
                    <p className="card-subtitle mb-2 text-muted">Count Down: {item.countDown} s</p>
                    <p className="card-subtitle mb-2 text-muted">Number of Flags: {item.numFlagged}</p>
                  </div>
                  <div style={{
                    marginBottom:'3px',
                    marginLeft:'3px',
                  }} className="col">
                    <div className="badge bg-info " style={{marginRight:'2px'}}>{item.categories}</div>
                  </div>
                  <div className="card-footer bg-transparent">
                    <div>
                      <span>
                        Current Bid: ${item.bidAmt} | Buy Now Price: $
                        {item.buyNowPrice}
                      </span>
                      <div className="mt-3">
                        <div className="input-group mb-3">
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Enter bid amount"
                            aria-label="Bid Amount"
                            value={bidAmounts[item.listingID] || ""}
                            onChange={(e) =>
                              handleBidAmountChange(
                                item.listingID,
                                e.target.value
                              )
                            }
                          />
                          <div className="input-group-append ">
                            <button
                              className="btn btn-primary"
                              type="button"
                              onClick={() => handleBidSubmit(item.listingID)}
                            >
                              Place Bid
                            </button>
                          </div>
                        </div>
                      </div>
                      <div>
                        <button
                          className="btn btn-primary"
                          type="button"
                          onClick={() => handleBuyNow(item.listingID)}
                        >
                          Buy It Now
                        </button>
                        <button
                          className="btn btn-primary"
                          type="button"
                          onClick={() => handleFlag(item.listingID)}
                        >
                          Flag
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center">
            <p>No listings found. Please try a different search.</p>
          </div>
        )}
      </div>
    </>
  );
}

export default Listings;
