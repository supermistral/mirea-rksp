// SPDX-License-Identifier: GPL-3.0
        
pragma solidity ^0.8.19;

// This import is automatically injected by Remix
import "../contracts/tests.sol"; // this import is automatically injected by Remix.
import "../contracts/SecuritiesTrading.sol";
import "hardhat/console.sol";

// This import is required to use custom transaction context
// Although it may fail compilation in 'Solidity Compiler' plugin
// But it will work fine in 'Solidity Unit Testing' plugin
import "remix_accounts.sol";


// File name has to end with '_test.sol', this file can contain more than one testSuite contracts
contract SecuritiesTradingTest {
    SecuritiesTrading securitiesTrading;
    mapping(string => SecuritiesTrading.Stock) stocks;

    function beforeAll () public {
        securitiesTrading = new SecuritiesTrading();
    }

    function checkSenderIsOwner () public {
        Assert.equal(msg.sender, securitiesTrading.owner(), "Sender should be owner");
    }

    function checkAddStock () public {
        securitiesTrading.addStock("Item1", 1, 5);
        stocks["Item1"] = SecuritiesTrading.Stock(1, 5);

        (uint256 price, uint256 quantity) = securitiesTrading.stocks("Item1");

        Assert.equal(price, uint256(1), "Price should be correct");
        Assert.equal(quantity, uint256(5), "Quantuty should be correct");
    }
}
    