// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title 0xAUTEUR — Onchain payment and receipting for AUTEUR film production
/// @notice deposit() funds an agent budget; spend() emits SpendReceipt with IPFS CID
contract auteur {

    struct Receipt {
        string taskId;
        uint256 amount;
        uint256 timestamp;
        string cid;
    }

    mapping(address => uint256) public budgets;
    mapping(address => Receipt[]) public spendLog;

    uint256 public totalSpend;
    uint256 public receiptCount;

    event Deposited(address indexed agentId, uint256 amount);
    event SpendReceipt(
        address indexed agentId,
        string taskId,
        uint256 amount,
        uint256 timestamp,
        string cid
    );
    event Withdrawn(address indexed agentId, uint256 amount);

    function deposit(address agentId) external payable {
        require(msg.value > 0, "Must deposit > 0");
        budgets[agentId] += msg.value;
        emit Deposited(agentId, msg.value);
    }

    function spend(
        address agentId,
        string calldata taskId,
        uint256 amount,
        string calldata cid
    ) external {
        require(budgets[agentId] >= amount, "Insufficient budget");
        require(bytes(taskId).length > 0, "taskId required");
        require(bytes(cid).length > 0, "CID required");

        budgets[agentId] -= amount;
        totalSpend += amount;
        receiptCount++;

        Receipt memory r = Receipt({
            taskId: taskId,
            amount: amount,
            timestamp: block.timestamp,
            cid: cid
        });
        spendLog[agentId].push(r);

        emit SpendReceipt(agentId, taskId, amount, block.timestamp, cid);
    }

    function getLog(address agentId) external view returns (Receipt[] memory) {
        return spendLog[agentId];
    }

    function getReceiptCount(address agentId) external view returns (uint256) {
        return spendLog[agentId].length;
    }

    function withdraw(uint256 amount) external {
        require(budgets[msg.sender] >= amount, "Insufficient budget");
        budgets[msg.sender] -= amount;
        (bool ok, ) = payable(msg.sender).call{value: amount}("");
        require(ok, "Transfer failed");
        emit Withdrawn(msg.sender, amount);
    }

    function withdrawAll() external {
        uint256 bal = budgets[msg.sender];
        require(bal > 0, "No balance");
        budgets[msg.sender] = 0;
        (bool ok, ) = payable(msg.sender).call{value: bal}("");
        require(ok, "Transfer failed");
        emit Withdrawn(msg.sender, bal);
    }
}
