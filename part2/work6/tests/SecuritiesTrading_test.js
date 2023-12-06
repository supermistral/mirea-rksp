const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SecuritiesTrading", function () {
  let owner;
  let acc1;
  let stock;

  beforeEach(async function() {
    [owner, acc1] = await ethers.getSigners();
    const SecuritiesTrading = await ethers.getContractFactory("SecuritiesTrading", owner);
    stock = await SecuritiesTrading.deploy();
  }); 

  it("Owner is set", async function() {
    expect(await stock.owner()).to.equal(await owner.getAddress());
  });

  it("Owner can add stock", async function() {
    await stock.connect(owner).addStock("test", 1, 200);

    const containedStock = await stock.connect(owner).stocks("test");
    expect(containedStock.price).to.equal(1);
    expect(containedStock.quantity).to.equal(200);
  });

  it("Non-owner can't add stock", async function() {
    await expect(stock.connect(acc1).addStock("test", 1, 200)).to.be.revertedWith("Only owner allowed");
  });

  it("Non-owner can buy stock", async function() {
    await stock.connect(owner).addStock("test", 1, 200);
  
    await stock.connect(acc1).buyStock("test", 2);
  });

  it("Owner can't buy stock", async function() {
    await stock.connect(owner).addStock(
      "test2",
      ethers.utils.parseUnits("20.0", "ether"), 200
    );

    await expect(stock.connect(acc1).buyStock("test2", 400)).to.be.revertedWith("Too big quantity");
  });

  it("Non-owner can sell stock", async function() {
    await stock.connect(owner).addStock("test", 1, 200);
    await stock.connect(acc1).buyStock("test", 5);
  
    await expect(stock.connect(acc1).sellStock("test", 5));
  });

  it("Owner can update stock price", async function() {
    await stock.connect(owner).addStock("test", 1, 200);

    await stock.connect(owner).updateStockPrice("test", 5);

    const containedStock = await stock.connect(owner).stocks("test");
    expect(containedStock.price).to.equal(5);
  });

  it("Non-owner can't update stock price", async function() {
    await stock.connect(owner).addStock("test", 1, 200);

    await expect(stock.connect(acc1).updateStockPrice("test", 5)).to.be.revertedWith("Only owner allowed");
  });
});
