//SPDX-License-Identifier: MIT
/// @title DEX with staking functionality
/// @author etorelan
/// @notice Minimum viable DEX based on Scaffold-ETH's DEX Challenge
pragma solidity ^0.8.13;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract InDex {
    ERC20 public token;
    uint256 totalLiquidity;
    mapping(address => uint256) liquidity;

    mapping(address => uint256[]) public stakeLock;
    mapping(address => uint256[]) public stakeAmount;

    event SwappedToken(uint256 token, uint256 _token);

    constructor(address _tokenAddress) {
        token = ERC20(_tokenAddress);
    }

    function start(uint256 _tokens) public payable {
        require(totalLiquidity <= 0, "Contract balance is already set");
        require(_tokens > 0, "Starting token amount cannot be 0");
        totalLiquidity = address(this).balance;
        liquidity[msg.sender] = totalLiquidity;
        require(
            token.transferFrom(msg.sender, address(this), _tokens),
            "ERC20 transfer failed"
        );
        emit SwappedToken(
            token.balanceOf(address(this)),
            address(this).balance
        );
    }

    function getPrice(
        uint256 _fromAmount,
        uint256 _fromReserve,
        uint256 _to_reserve
    ) public view returns (uint256) {
        uint256 fromAmountWithFee = _fromAmount * 997;
        uint256 numerator = fromAmountWithFee * _to_reserve;
        uint256 denumerator = _fromReserve * 1000 + fromAmountWithFee;
        return numerator / denumerator;
    }

    function ethToToken() public payable {
        uint256 swappedTokens = getPrice(
            msg.value,
            address(this).balance - msg.value,
            token.balanceOf(address(this))
        );
        require(token.transfer(msg.sender, swappedTokens));
        emit SwappedToken(swappedTokens, 0);
    }

    function tokenToEth(uint256 _tokens) public payable {
        uint256 swappedETH = getPrice(
            _tokens,
            token.balanceOf(address(this)),
            address(this).balance
        );
        payable(msg.sender).transfer(swappedETH);
        require(token.transferFrom(msg.sender, address(this), _tokens));
        emit SwappedToken(swappedETH, 0);
    }

    function stake() public payable {
        uint256 eth_reserve = address(this).balance - (msg.value);
        uint256 token_reserve = token.balanceOf(address(this));
        uint256 token_amount = ((msg.value * (token_reserve)) / eth_reserve) +
            (1);
        uint256 liquidity_minted = (msg.value * (totalLiquidity)) / eth_reserve;
        liquidity[msg.sender] += liquidity_minted;
        totalLiquidity += liquidity_minted;
        uint256 timeLock = block.timestamp; //+ 1209600; //two weeks in seconds
        stakeLock[msg.sender].push(timeLock);
        stakeAmount[msg.sender].push(token_amount);
        require(token.transferFrom(msg.sender, address(this), token_amount));
        emit SwappedToken(liquidity_minted, token_amount);
    }

    function withdraw(uint256 amount) public {
        require(
            getWithdrawAmount() >= amount,
            "Requested withdraw amount is higher than available amount. Check stakeLock or stakeAmount mappings and refer to getWithdrawAmount()"
        );

        uint256 token_reserve = token.balanceOf(address(this));
        uint256 eth_amount = (amount * (address(this).balance)) /
            totalLiquidity;
        uint256 token_amount = (amount * (token_reserve)) / totalLiquidity;
        liquidity[msg.sender] -= eth_amount;
        totalLiquidity -= eth_amount;
        payable(msg.sender).transfer(eth_amount);
        require(token.transfer(msg.sender, token_amount));
        emit SwappedToken(eth_amount, token_amount);
    }

    function getWithdrawAmount() public view returns (uint256) {
        uint256 withdrawIndex = stakeLock[msg.sender].length;

        for (uint256 i = 0; i < stakeLock[msg.sender].length; i++) {
            if (stakeLock[msg.sender][i] <= block.timestamp) {
                withdrawIndex = i;
            }
        }
        require(
            withdrawIndex < stakeLock[msg.sender].length,
            "TOKEN WITHDRAWAL: You cannot withdraw any tokens yet"
        );

        uint256 maxWithdrawAmount = 0;
        for (uint256 i = 0; i <= withdrawIndex; i++) {
            maxWithdrawAmount += stakeAmount[msg.sender][i];
        }

        return maxWithdrawAmount;
    }
}
