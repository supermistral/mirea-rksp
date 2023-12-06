// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.19;

contract SecuritiesTrading {
    address public owner;

    struct Stock {
        uint256 price;
        uint256 quantity;
    }

    mapping(string => Stock) public stocks;
    mapping(address => mapping(string => uint256)) public balances;

    event StockBought(address buyer, string stockName, uint256 price, uint256 quantity);
    event StockSold(address seller, string stockName, uint256 price, uint256 quantity);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner allowed");
        _;
    }

    function buyStock(string memory stockName, uint256 quantity) public payable {
        Stock memory stock = stocks[stockName];

        require(stock.price > 0, "Stock does not exist");
        require(stock.quantity >= quantity, "Too big quantity");

        stocks[stockName].quantity -= quantity;
        balances[msg.sender][stockName] += quantity;

        emit StockBought(msg.sender, stockName, stock.price, quantity);
    }

    function sellStock(string memory stockName, uint256 quantity) public {
        Stock memory stock = stocks[stockName];

        require(stock.price > 0, "Stock does not exist");
        require(balances[msg.sender][stockName] >= quantity, "Lack of stock balance");

        balances[msg.sender][stockName] -= quantity;
        payable(msg.sender).transfer(stock.price * quantity);

        emit StockSold(msg.sender, stockName, stock.price, quantity);
    }

    function addStock(string memory stockName, uint256 price, uint256 quantity) public onlyOwner {
        Stock memory stock = stocks[stockName];

        require(stock.price == 0, "Stock already exists.");

        stocks[stockName] = Stock(price, quantity);
    }

    function updateStockPrice(string memory stockName, uint256 price) public onlyOwner {
        Stock memory stock = stocks[stockName];

        require(stock.price > 0, "Stock does not exist");

        stocks[stockName].price = price;
    }

    function withdraw() public onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}